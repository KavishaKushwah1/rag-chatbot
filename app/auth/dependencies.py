"""
FastAPI dependency that verifies the Authorization: Bearer <token> header
against Supabase, then looks up the user's department to derive their
allowed permission tiers. Endpoints depend on this instead of trusting
any client-supplied permission list.
"""
from __future__ import annotations
from dataclasses import dataclass

from fastapi import Header, HTTPException

from app.auth.supabase_client import get_anon_client, get_service_client
from app.auth.permissions import permissions_for_department


@dataclass
class CurrentUser:
    user_id: str
    email: str | None
    department: str
    permissions: list[str]


def get_current_user(authorization: str = Header(...)) -> CurrentUser:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    token = authorization.removeprefix("Bearer ").strip()

    anon_client = get_anon_client()
    try:
        user_response = anon_client.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if not user_response or not user_response.user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = user_response.user

    service_client = get_service_client()
    profile_result = (
        service_client.table("profiles").select("department").eq("id", user.id).single().execute()
    )

    department = "public"
    if profile_result.data:
        department = profile_result.data.get("department", "public")

    return CurrentUser(
        user_id=user.id,
        email=user.email,
        department=department,
        permissions=permissions_for_department(department),
    )