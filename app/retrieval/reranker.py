"""
Cross-encoder reranking: hybrid search gets us a decent candidate set fast,
but bi-encoder similarity (dense) and BM25 (sparse) both score query and
document independently. A cross-encoder scores the (query, document) PAIR
jointly, which is slower but far more precise — so we only run it on the
top-N candidates from hybrid search, not the whole collection.
"""
from __future__ import annotations
from fastembed.rerank.cross_encoder import TextCrossEncoder

_reranker: TextCrossEncoder | None = None


def get_reranker() -> TextCrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = TextCrossEncoder(model_name="Xenova/ms-marco-MiniLM-L-6-v2")
    return _reranker


def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """
    candidates: list of dicts each containing at least a "text" key.
    Returns the same dicts, sorted by rerank score descending, truncated to top_k,
    with a "rerank_score" key added.
    """
    if not candidates:
        return []

    model = get_reranker()
    documents = [c["text"] for c in candidates]
    scores = list(model.rerank(query, documents))

    for candidate, score in zip(candidates, scores):
        candidate["rerank_score"] = float(score)

    ranked = sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
    return ranked[:top_k]