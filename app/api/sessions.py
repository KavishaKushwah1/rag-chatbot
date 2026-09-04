"""
GET /sessions — list this user's past chat sessions (most recent first)
GET /sessions/{session_id}/messages — full message history for one session
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user, CurrentUser
from app.auth.supabase_client import get_service_client

router = APIRouter()


@router.get("/sessions")
def list_sessions(current_user: CurrentUser = Depends(get_current_user)):
    client = get_service_client()

    sessions_result = (
        client.table("chat_sessions")
        .select("id, created_at")
        .eq("user_id", current_user.user_id)
        .order("created_at", desc=True)
        .execute()
    )
    sessions = sessions_result.data or []

    # Attach a short preview (first user message) for each session so the
    # sidebar can show something more useful than a raw UUID.
    out = []
    for s in sessions:
        first_msg = (
            client.table("chat_messages")
            .select("content")
            .eq("session_id", s["id"])
            .eq("role", "user")
            .order("created_at", desc=False)
            .limit(1)
            .execute()
        )
        preview = first_msg.data[0]["content"] if first_msg.data else "(empty session)"
        out.append({"session_id": s["id"], "created_at": s["created_at"], "preview": preview[:60]})

    return out


@router.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: str, current_user: CurrentUser = Depends(get_current_user)):
    client = get_service_client()

    # Ownership check — never let a user load another user's session by guessing an id
    session_check = (
        client.table("chat_sessions")
        .select("id")
        .eq("id", session_id)
        .eq("user_id", current_user.user_id)
        .execute()
    )
    if not session_check.data:
        raise HTTPException(status_code=404, detail="Session not found")

    messages_result = (
        client.table("chat_messages")
        .select("role, content, created_at")
        .eq("session_id", session_id)
        .order("created_at", desc=False)
        .execute()
    )
    return messages_result.data or []