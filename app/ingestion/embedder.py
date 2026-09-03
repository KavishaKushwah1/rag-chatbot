"""
Local embeddings via FastEmbed (ONNX runtime) — no PyTorch, so this
comfortably fits Render's 512MB free-tier RAM limit later.

Dense = semantic similarity (BAAI/bge-small-en-v1.5).
Sparse = keyword/BM25-style matching (Qdrant/bm25), catches exact terms
(product names, error codes, policy numbers) that dense embeddings can miss.
"""
from __future__ import annotations
from fastembed import TextEmbedding, SparseTextEmbedding
from fastembed.sparse.sparse_embedding_base import SparseEmbedding

from app.config import settings

_dense_model: TextEmbedding | None = None
_sparse_model: SparseTextEmbedding | None = None


def get_dense_embedder() -> TextEmbedding:
    global _dense_model
    if _dense_model is None:
        _dense_model = TextEmbedding(model_name=settings.embedding_model)
    return _dense_model


def get_sparse_embedder() -> SparseTextEmbedding:
    global _sparse_model
    if _sparse_model is None:
        _sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")
    return _sparse_model


def embed_texts_dense(texts: list[str]) -> list[list[float]]:
    model = get_dense_embedder()
    return [vec.tolist() for vec in model.embed(texts)]


def embed_texts_sparse(texts: list[str]) -> list[SparseEmbedding]:
    model = get_sparse_embedder()
    return list(model.embed(texts))


def embed_query_dense(text: str) -> list[float]:
    return embed_texts_dense([text])[0]


def embed_query_sparse(text: str) -> SparseEmbedding:
    return embed_texts_sparse([text])[0]