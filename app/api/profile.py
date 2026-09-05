"""
GET   /me — return the current user's profile (email, display_name, department)
PATCH /me — update display_name
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas import ProfileUpdateRequest
from app.auth.dependencies import get_current_user, CurrentUser
from app.auth.supabase_client import get_service_client

router = APIRouter()


@router.get("/me")
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    client = get_service_client()
    result = (
        client.table("profiles")
        .select("display_name, department")
        .eq("id", current_user.user_id)
        .single()
        .execute()
    )
    display_name = (result.data or {}).get("display_name")
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "display_name": display_name,
        "department": current_user.department,
    }


@router.patch("/me")
def update_me(body: ProfileUpdateRequest, current_user: CurrentUser = Depends(get_current_user)):
    client = get_service_client()
    name = body.display_name.strip()[:80]
    client.table("profiles").update({"display_name": name}).eq("id", current_user.user_id).execute()
    return {"ok": True, "display_name": name}