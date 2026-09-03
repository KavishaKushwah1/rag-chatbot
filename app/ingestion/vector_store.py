"""
Thin wrapper around Qdrant for creating the collection and upserting
chunks with metadata (permission tags live here — this is what Phase 4's
ACL filtering will query against).
"""
from __future__ import annotations
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.config import settings

COLLECTION_NAME = "kb_chunks"
VECTOR_SIZE = 384  # matches BAAI/bge-small-en-v1.5


def get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)


def ensure_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        return
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


def upsert_chunks(client: QdrantClient, chunks_with_vectors: list[tuple]) -> None:
    """chunks_with_vectors: list of (Chunk, embedding_vector) tuples"""
    points = []
    for chunk, vector in chunks_with_vectors:
        points.append(
            PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id)),
                vector=vector,
                payload={
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "source": chunk.source,
                    "permission": chunk.permission,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                },
            )
        )
    client.upsert(collection_name=COLLECTION_NAME, points=points)