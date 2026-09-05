"""
Runs known relevant/irrelevant queries through the reranker so you can
pick a real threshold. Deliberately biased toward permissive: since the
LLM + system prompt is the second, smarter line of defense against
irrelevant context, this threshold only needs to reject clear garbage —
not make the final call. Run after ingestion.
"""
from app.retrieval.hybrid_search import hybrid_search

CASES = [
    ("What is the PTO carryover policy?", True),
    ("How do I roll back a bad deployment?", True),
    ("What are the pricing tiers?", True),
    ("Do students get a discount?", True),
    ("What is the remote work policy?", True),
    ("What is the incident response process for SEV1?", True),
    ("What is the CEO's favorite color?", False),
    ("What's the weather like today?", False),
    ("Write me a poem about the ocean", False),
    ("What is Acme's stock ticker symbol?", False),
]


def main():
    relevant_scores, irrelevant_scores = [], []

    for query, should_match in CASES:
        results = hybrid_search(query, top_k_final=1)
        top_score = results[0]["rerank_score"] if results else float("-inf")
        label = "RELEVANT" if should_match else "IRRELEVANT"
        print(f"[{label:10}] score={top_score:7.3f}  query={query!r}")
        (relevant_scores if should_match else irrelevant_scores).append(top_score)

    r_min, i_max = min(relevant_scores), max(irrelevant_scores)
    print(f"\nRelevant queries   -> min={r_min:.3f}  max={max(relevant_scores):.3f}")
    print(f"Irrelevant queries -> min={min(irrelevant_scores):.3f}  max={i_max:.3f}")

    if i_max >= r_min:
        print("\n⚠️  Score distributions OVERLAP — no threshold perfectly separates them.")
        print("   Biasing toward permissive: rely on the LLM's own 'I don't know' instruction")
        print("   as the real filter, not this pre-filter.")
        suggested = r_min - 0.5
    else:
        suggested = (r_min + i_max) / 2

    print(f"\nSuggested threshold: {suggested:.3f}  (never higher than weakest relevant score)")
    print("Set MIN_RELEVANCE_SCORE in .env to this value.")


if __name__ == "__main__":
    main()