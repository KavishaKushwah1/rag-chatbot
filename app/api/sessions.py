"""
GET    /sessions                      — list this user's sessions (pinned first, then recent)
GET    /sessions/{session_id}/messages — full message history for one session
PATCH  /sessions/{session_id}          — rename and/or pin/unpin
DELETE /sessions/{session_id}          — delete a session (cascades to its messages)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import SessionUpdateRequest
from app.auth.dependencies import get_current_user, CurrentUser
from app.auth.supabase_client import get_service_client

router = APIRouter()


def _assert_owns_session(client, session_id: str, user_id: str) -> None:
    result = (
        client.table("chat_sessions")
        .select("id")
        .eq("id", session_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/sessions")
def list_sessions(current_user: CurrentUser = Depends(get_current_user)):
    client = get_service_client()

    sessions_result = (
        client.table("chat_sessions")
        .select("id, created_at, title, pinned")
        .eq("user_id", current_user.user_id)
        .order("pinned", desc=True)
        .order("created_at", desc=True)
        .execute()
    )
    sessions = sessions_result.data or []

    out = []
    for s in sessions:
        preview = s.get("title")
        if not preview:
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

        out.append(
            {
                "session_id": s["id"],
                "created_at": s["created_at"],
                "preview": preview[:60],
                "pinned": s["pinned"],
            }
        )

    return out


@router.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: str, current_user: CurrentUser = Depends(get_current_user)):
    client = get_service_client()
    _assert_owns_session(client, session_id, current_user.user_id)

    messages_result = (
        client.table("chat_messages")
        .select("role, content, created_at, sources")
        .eq("session_id", session_id)
        .order("created_at", desc=False)
        .execute()
    )
    return messages_result.data or []


@router.patch("/sessions/{session_id}")
def update_session(
    session_id: str, body: SessionUpdateRequest, current_user: CurrentUser = Depends(get_current_user)
):
    client = get_service_client()
    _assert_owns_session(client, session_id, current_user.user_id)

    updates = {}
    if body.title is not None:
        updates["title"] = body.title.strip()[:100] or None
    if body.pinned is not None:
        updates["pinned"] = body.pinned

    if not updates:
        raise HTTPException(status_code=400, detail="Nothing to update")

    client.table("chat_sessions").update(updates).eq("id", session_id).execute()
    return {"ok": True}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, current_user: CurrentUser = Depends(get_current_user)):
    client = get_service_client()
    _assert_owns_session(client, session_id, current_user.user_id)

    client.table("chat_sessions").delete().eq("id", session_id).execute()
    return {"ok": True}