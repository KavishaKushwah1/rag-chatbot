"""
Long-term memory: durable facts about a user, stored as vectors in a
dedicated Qdrant collection (separate from the KB), namespaced by user_id
via a payload filter. Persists across sessions and logins.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone

from qdrant_client import models

from app.ingestion.embedder import embed_query_dense
from app.ingestion.vector_store import get_client, VECTOR_SIZE

MEMORY_COLLECTION = "user_memories"


def ensure_memory_collection() -> None:
    client = get_client()
    if not client.collection_exists(MEMORY_COLLECTION):
        client.create_collection(
            collection_name=MEMORY_COLLECTION,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
        )


def store_memory(user_id: str, fact: str) -> None:
    client = get_client()
    ensure_memory_collection()
    vector = embed_query_dense(fact)
    client.upsert(
        collection_name=MEMORY_COLLECTION,
        points=[
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "user_id": user_id,
                    "fact": fact,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        ],
    )


def retrieve_memories(user_id: str, query: str, top_k: int = 3) -> list[str]:
    client = get_client()
    if not client.collection_exists(MEMORY_COLLECTION):
        return []

    vector = embed_query_dense(query)
    results = client.query_points(
        collection_name=MEMORY_COLLECTION,
        query=vector,
        query_filter=models.Filter(
            must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
        ),
        limit=top_k,
    )
    return [point.payload["fact"] for point in results.points]