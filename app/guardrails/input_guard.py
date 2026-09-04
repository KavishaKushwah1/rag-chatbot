"""
Lightweight checks on the user's own query. We don't block on these (a
user is entitled to type "ignore instructions" as a literal question
about prompt injection) — this is for logging/observability so we can
see attempted misuse. Also enforces a basic length cap to prevent
degenerate/abuse inputs from blowing up token costs.
"""
from __future__ import annotations
import logging

from app.guardrails.injection_detector import detect_injection

logger = logging.getLogger("uvicorn.error")

MAX_QUERY_LENGTH = 2000


def validate_query(query: str) -> str:
    """Returns the (possibly truncated) query. Raises ValueError if empty."""
    query = query.strip()
    if not query:
        raise ValueError("Query cannot be empty")

    if len(query) > MAX_QUERY_LENGTH:
        logger.warning(f"Query truncated from {len(query)} to {MAX_QUERY_LENGTH} chars")
        query = query[:MAX_QUERY_LENGTH]

    matches = detect_injection(query)
    if matches:
        logger.info(f"User query contains injection-like phrasing (logged, not blocked): {matches}")

    return query