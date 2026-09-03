"""
Hybrid retrieval: runs dense + sparse search against Qdrant in a single
prefetch/fusion query (Reciprocal Rank Fusion), then reranks the fused
candidates with a cross-encoder for the final result set.

ACL note (Phase 4 hooks in here): the `permission_filter` param already
exists so access control plugs straight into the Qdrant query itself,
not as a post-filter after retrieval.
"""
from __future__ import annotations

from qdrant_client import models

from app.ingestion.embedder import embed_query_dense, embed_query_sparse
from app.ingestion.vector_store import get_client, COLLECTION_NAME


def hybrid_search(
    query: str,
    top_k_candidates: int = 20,
    top_k_final: int = 5,
    permission_filter: list[str] | None = None,
) -> list[dict]:
    from app.retrieval.reranker import rerank  # local import avoids loading reranker on ingest

    client = get_client()

    dense_vector = embed_query_dense(query)
    sparse_embedding = embed_query_sparse(query)

    qdrant_filter = None
    if permission_filter:
        qdrant_filter = models.Filter(
            must=[models.FieldCondition(key="permission", match=models.MatchAny(any=permission_filter))]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            models.Prefetch(
                query=dense_vector,
                using="dense",
                limit=top_k_candidates,
                filter=qdrant_filter,
            ),
            models.Prefetch(
                query=models.SparseVector(
                    indices=sparse_embedding.indices.tolist(),
                    values=sparse_embedding.values.tolist(),
                ),
                using="sparse",
                limit=top_k_candidates,
                filter=qdrant_filter,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=top_k_candidates,
    )

    candidates = [
        {
            "chunk_id": point.payload["chunk_id"],
            "doc_id": point.payload["doc_id"],
            "source": point.payload["source"],
            "permission": point.payload["permission"],
            "text": point.payload["text"],
            "fusion_score": point.score,
        }
        for point in results.points
    ]

    return rerank(query, candidates, top_k=top_k_final)