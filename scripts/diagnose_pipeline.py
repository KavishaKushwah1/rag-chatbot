"""
End-to-end pipeline diagnostic. Checks every stage independently so a
failure can be pinpointed to indexing, embeddings, fusion, reranking, or
the confidence threshold — instead of guessing.

Usage: python scripts\\diagnose_pipeline.py
"""
from app.ingestion.vector_store import get_client, COLLECTION_NAME
from app.retrieval.hybrid_search import hybrid_search
from app.config import settings

CHECK_QUERIES = [
    "What is the PTO carryover policy?",
    "How do I roll back a bad deployment?",
    "What are the pricing tiers?",
    "What is the remote work policy?",
]


def main():
    print("=" * 70)
    print("STAGE 1: Qdrant connectivity + collection health")
    print("=" * 70)
    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):
        print(f"❌ Collection '{COLLECTION_NAME}' does NOT exist. Run: python scripts\\ingest.py")
        return

    info = client.get_collection(COLLECTION_NAME)
    print(f"✅ Collection exists. Points: {info.points_count}")
    if info.points_count == 0:
        print("❌ Collection is EMPTY. Run: python scripts\\ingest.py")
        return

    vectors_config = info.config.params.vectors
    sparse_config = info.config.params.sparse_vectors
    print(f"   Dense vectors configured: {bool(vectors_config)}")
    print(f"   Sparse vectors configured: {bool(sparse_config)}")

    print(f"\nCurrent MIN_RELEVANCE_SCORE = {settings.min_relevance_score}")

    print("\n" + "=" * 70)
    print("STAGE 2-4: Fusion retrieval -> Reranking -> Threshold gate")
    print("=" * 70)
    for query in CHECK_QUERIES:
        debug = hybrid_search(query, top_k_final=5, return_debug=True)
        fusion = debug["fusion_candidates"]
        reranked = debug["reranked"]

        print(f"\nQuery: {query!r}")
        print(f"  Fusion candidates retrieved: {len(fusion)}")
        if not fusion:
            print("  ❌ ZERO fusion candidates — dense+sparse search itself found nothing. "
                  "Check embeddings/indexing, not the threshold.")
            continue

        print(f"  Top reranked scores: {[round(r['rerank_score'], 3) for r in reranked[:5]]}")
        passing = [r for r in reranked if r["rerank_score"] >= settings.min_relevance_score]
        if not passing:
            print(f"  ❌ ALL results REJECTED by threshold ({settings.min_relevance_score}). "
                  f"Best score was {max(r['rerank_score'] for r in reranked):.3f} — "
                  f"threshold is too strict for this reranker's score range.")
        else:
            print(f"  ✅ {len(passing)}/{len(reranked)} results pass threshold. "
                  f"Top match: {passing[0]['source']} ({passing[0]['rerank_score']:.3f})")

    print("\n" + "=" * 70)
    print("Diagnosis complete.")


if __name__ == "__main__":
    main()