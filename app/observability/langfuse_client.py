"""
Thin wrapper around Langfuse's v4 client. v4 reads LANGFUSE_PUBLIC_KEY /
LANGFUSE_SECRET_KEY / LANGFUSE_BASE_URL from the environment directly, so
we set them from our own settings object once at import time, then hand
back the singleton client via get_client().
"""
from __future__ import annotations
import os

from app.config import settings

if settings.langfuse_public_key:
    os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.langfuse_public_key)
if settings.langfuse_secret_key:
    os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.langfuse_secret_key)
os.environ.setdefault("LANGFUSE_BASE_URL", settings.langfuse_base_url)

_enabled = bool(settings.langfuse_public_key and settings.langfuse_secret_key)


def is_enabled() -> bool:
    return _enabled


def get_langfuse():
    from langfuse import get_client
    return get_client()