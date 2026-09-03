"""
Usage: python scripts/query.py "What is the PTO carryover policy?"
Optional: --permissions public hr   (defaults to all tiers, i.e. no filter)
"""
import argparse
from app.retrieval.hybrid_search import hybrid_search


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    parser.add_argument("--permissions", nargs="*", default=None)
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args()

    results = hybrid_search(
        query=args.query,
        top_k_final=args.top_k,
        permission_filter=args.permissions,
    )

    print(f'\nQuery: "{args.query}"')
    print(f"Permission filter: {args.permissions or 'none (all tiers)'}\n")
    print("-" * 70)
    for i, r in enumerate(results, 1):
        print(f"[{i}] score={r['rerank_score']:.4f}  source={r['source']}  permission={r['permission']}")
        print(f"    {r['text'][:200]}...")
        print("-" * 70)


if __name__ == "__main__":
    main()