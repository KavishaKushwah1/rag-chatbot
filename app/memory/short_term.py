"""
Short-term memory: recent turns of the current session, stored in
Supabase Postgres and injected into the prompt as chat history.
"""
from __future__ import annotations

from app.auth.supabase_client import get_service_client

MAX_HISTORY_TURNS = 6  # 6 user+assistant pairs = 12 messages


def ensure_session(session_id: str, user_id: str) -> None:
    """Creates the session row if it doesn't already exist (idempotent)."""
    client = get_service_client()
    existing = client.table("chat_sessions").select("id").eq("id", session_id).execute()
    if not existing.data:
        client.table("chat_sessions").insert({"id": session_id, "user_id": user_id}).execute()


def get_recent_messages(session_id: str, limit: int = MAX_HISTORY_TURNS * 2) -> list[dict]:
    client = get_service_client()
    result = (
        client.table("chat_messages")
        .select("role, content")
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    rows = result.data or []
    rows.reverse()  # chronological order for prompt building
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def save_message(session_id: str, user_id: str, role: str, content: str, sources: list[dict] | None = None) -> None:
    client = get_service_client()
    client.table("chat_messages").insert(
        {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "sources": sources or [],
        }
    ).execute()