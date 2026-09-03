"""
Local embeddings via FastEmbed (ONNX runtime) — no PyTorch, so this
comfortably fits Render's 512MB free-tier RAM limit later.
"""
from __future__ import annotations
from fastembed import TextEmbedding

from app.config import settings

_model: TextEmbedding | None = None


def get_embedder() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=settings.embedding_model)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedder()
    return [vec.tolist() for vec in model.embed(texts)]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]