"""
Thin wrapper around Qdrant. Collection stores TWO vectors per point:
  - "dense": semantic embedding (384-dim, cosine)
  - "sparse": BM25-style sparse embedding (keyword matching)
Both are queried together in Phase 2's hybrid search.
"""
from __future__ import annotations
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
    SparseVector,
    PointStruct,
)

from app.config import settings

COLLECTION_NAME = "kb_chunks"
VECTOR_SIZE = 384  # matches BAAI/bge-small-en-v1.5


def get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key, port=443)

def recreate_collection(client: QdrantClient) -> None:
    """Drops and recreates the collection with dense + sparse vector support."""
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams(),
        },
    )
    _ensure_permission_index(client)


def _ensure_permission_index(client: QdrantClient) -> None:
    """
    Qdrant Cloud requires an explicit payload index before filtering on a
    field with MatchAny/FieldCondition — unlike local Docker Qdrant, which
    allows unindexed filtering by default. Without this, every ACL-filtered
    query fails with a 400 Bad Request.
    """
    from qdrant_client.models import PayloadSchemaType

    try:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="permission",
            field_schema=PayloadSchemaType.KEYWORD,
        )
    except Exception:
        pass  # index likely already exists — safe to ignore


def ensure_collection(client: QdrantClient) -> None:
    if not client.collection_exists(COLLECTION_NAME):
        recreate_collection(client)
    _ensure_permission_index(client)


def upsert_chunks(client: QdrantClient, rows: list[tuple]) -> None:
    """rows: list of (Chunk, dense_vector, sparse_embedding) tuples"""
    points = []
    for chunk, dense_vector, sparse_embedding in rows:
        points.append(
            PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id)),
                vector={
                    "dense": dense_vector,
                    "sparse": SparseVector(
                        indices=sparse_embedding.indices.tolist(),
                        values=sparse_embedding.values.tolist(),
                    ),
                },
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