"""
POST /messages/{message_id}/feedback — thumbs up/down on an assistant
message. One rating per user per message (upsert on conflict).
"""
from __future__ import annotations
from pydantic import BaseModel
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user, CurrentUser
from app.auth.supabase_client import get_service_client

router = APIRouter()


class FeedbackRequest(BaseModel):
    rating: str  # "up" | "down"


@router.post("/messages/{message_id}/feedback")
def submit_feedback(message_id: str, body: FeedbackRequest, current_user: CurrentUser = Depends(get_current_user)):
    client = get_service_client()
    client.table("message_feedback").upsert(
        {"message_id": message_id, "user_id": current_user.user_id, "rating": body.rating},
        on_conflict="message_id,user_id",
    ).execute()
    return {"ok": True}