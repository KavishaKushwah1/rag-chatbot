"""
Blocks the query before it ever reaches retrieval or the LLM when it
matches a data-exfiltration or instruction-override pattern. This is a
hard stop, not a log-and-continue — unlike retrieved-document sanitizing
(which quotes-and-flags), a user's own direct request to dump secrets
gets refused outright.
"""
from __future__ import annotations
import logging

from app.guardrails.injection_detector import detect_injection

logger = logging.getLogger("uvicorn.error")

MAX_QUERY_LENGTH = 2000

REFUSAL_MESSAGE = (
    "I can't help with requests to reveal credentials, API keys, passwords, "
    "or other confidential access information."
)


class QueryBlockedError(ValueError):
    """Raised when a query is refused outright, before touching retrieval/LLM."""
    def __init__(self, message: str = REFUSAL_MESSAGE):
        super().__init__(message)
        self.message = message


def validate_query(query: str) -> str:
    query = query.strip()
    if not query:
        raise ValueError("Query cannot be empty")

    if len(query) > MAX_QUERY_LENGTH:
        logger.warning(f"Query truncated from {len(query)} to {MAX_QUERY_LENGTH} chars")
        query = query[:MAX_QUERY_LENGTH]

    matches = detect_injection(query)
    if matches:
        logger.warning(f"Blocked query matching injection/exfiltration patterns: {matches}")
        raise QueryBlockedError()

    return query