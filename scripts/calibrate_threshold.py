"""
Runs a set of queries with KNOWN relevant and irrelevant expected matches
against the reranker, prints scores, so you can pick a real threshold
instead of guessing. Run after ingestion.

Usage: python scripts\calibrate_threshold.py
"""
from app.retrieval.hybrid_search import hybrid_search

# (query, should_match) pairs — should_match=True means we expect a
# genuinely relevant chunk to come back; False means the query has
# nothing to do with the KB and SHOULD score low.
CASES = [
    ("What is the PTO carryover policy?", True),
    ("How do I roll back a bad deployment?", True),
    ("What are the pricing tiers?", True),
    ("Do students get a discount?", True),
    ("What is the CEO's favorite color?", False),
    ("What's the weather like today?", False),
    ("Write me a poem about the ocean", False),
    ("What is Acme's stock ticker symbol?", False),
]


def main():
    relevant_scores = []
    irrelevant_scores = []

    for query, should_match in CASES:
        results = hybrid_search(query, top_k_final=1)
        top_score = results[0]["rerank_score"] if results else float("-inf")
        label = "RELEVANT" if should_match else "IRRELEVANT"
        print(f"[{label:10}] score={top_score:7.3f}  query={query!r}")

        if should_match:
            relevant_scores.append(top_score)
        else:
            irrelevant_scores.append(top_score)

    print("\n--- Summary ---")
    print(f"Relevant queries   -> min={min(relevant_scores):.3f}  max={max(relevant_scores):.3f}")
    print(f"Irrelevant queries -> min={min(irrelevant_scores):.3f}  max={max(irrelevant_scores):.3f}")

    suggested = (min(relevant_scores) + max(irrelevant_scores)) / 2
    print(f"\nSuggested threshold (midpoint): {suggested:.3f}")
    print("Set this as min_relevance_score in .env or app/config.py")


if __name__ == "__main__":
    main()