"""
Two Supabase clients with different privilege levels:
- anon client: used to verify a user's JWT (equivalent to what a frontend would use)
- service client: used to read the profiles table with elevated privileges,
  bypassing RLS, since the backend is trusted infrastructure
"""
from __future__ import annotations
from supabase import create_client, Client

from app.config import settings

_anon_client: Client | None = None
_service_client: Client | None = None


def get_anon_client() -> Client:
    global _anon_client
    if _anon_client is None:
        if not settings.supabase_url or not settings.supabase_anon_key:
            raise RuntimeError("SUPABASE_URL / SUPABASE_ANON_KEY not set in .env")
        _anon_client = create_client(settings.supabase_url, settings.supabase_anon_key)
    return _anon_client


def get_service_client() -> Client:
    global _service_client
    if _service_client is None:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set in .env")
        _service_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _service_client