"""
Runs the golden set end-to-end through the real retrieval + generation
pipeline (same code path as production, not a mock), then scores the
results with Ragas metrics. Prints per-category breakdowns and writes a
CSV report.

Usage: python eval\\run_eval.py
Run manually / nightly CI — not on every commit, to avoid burning
through the Gemini free-tier rate limit.
"""
from __future__ import annotations
import csv
import sys
from datetime import datetime, timezone

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

sys.path.insert(0, ".")  # allow `python eval\run_eval.py` from repo root

from eval.golden_set import GOLDEN_SET
from eval.ragas_llm import get_ragas_llm, get_ragas_embeddings
from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.prompt_builder import build_messages
from app.llm.gemini_client import stream_completion

MIN_RELEVANCE_SCORE = -2.0


def generate_answer(question: str) -> tuple[str, list[str]]:
    """Runs the real pipeline: hybrid search -> prompt -> LLM. Returns (answer, contexts)."""
    results = hybrid_search(query=question, top_k_final=5)
    strong_results = [r for r in results if r["rerank_score"] >= MIN_RELEVANCE_SCORE]

    contexts = [r["text"] for r in strong_results]

    if not strong_results:
        return "I don't have enough information to answer that.", contexts

    messages = build_messages(question, strong_results)
    answer = "".join(stream_completion(messages))
    return answer, contexts


def main():
    print(f"Running eval on {len(GOLDEN_SET)} golden cases...\n")

    rows = []
    for i, case in enumerate(GOLDEN_SET, start=1):
        print(f"[{i}/{len(GOLDEN_SET)}] ({case['category']}) {case['question']}")
        answer, contexts = generate_answer(case["question"])
        rows.append(
            {
                "category": case["category"],
                "question": case["question"],
                "answer": answer,
                "contexts": contexts if contexts else ["(no context retrieved)"],
                "ground_truth": case["ground_truth"],
            }
        )

    dataset = Dataset.from_list(
        [
            {
                "question": r["question"],
                "answer": r["answer"],
                "contexts": r["contexts"],
                "ground_truth": r["ground_truth"],
            }
            for r in rows
        ]
    )

    print("\nScoring with Ragas (faithfulness, answer_relevancy, context_precision, context_recall)...")
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=get_ragas_llm(),
        embeddings=get_ragas_embeddings(),
    )

    scores_df = result.to_pandas()

    # Attach category back for per-category breakdown
    scores_df["category"] = [r["category"] for r in rows]

    print("\n=== Overall scores ===")
    for metric in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        if metric in scores_df.columns:
            print(f"{metric:20} {scores_df[metric].mean():.3f}")

    print("\n=== Per-category breakdown ===")
    for category in ["factual", "edge_case", "adversarial"]:
        subset = scores_df[scores_df["category"] == category]
        if subset.empty:
            continue
        print(f"\n{category.upper()} ({len(subset)} cases)")
        for metric in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
            if metric in subset.columns:
                print(f"  {metric:20} {subset[metric].mean():.3f}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = f"eval/reports/eval_{timestamp}.csv"
    import os
    os.makedirs("eval/reports", exist_ok=True)
    scores_df.to_csv(report_path, index=False)
    print(f"\nFull report written to {report_path}")


if __name__ == "__main__":
    main()