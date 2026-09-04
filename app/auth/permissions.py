"""
Maps a user's department to the set of document permission tiers they can
retrieve. This is the single source of truth for ACL — Phase 2's
hybrid_search() just takes whatever list this returns and filters the
Qdrant query with it.
"""
from __future__ import annotations

DEPARTMENT_TO_PERMISSIONS = {
    "public": ["public"],
    "hr": ["public", "hr"],
    "engineering": ["public", "engineering"],
    "admin": ["public", "hr", "engineering"],
}


def permissions_for_department(department: str) -> list[str]:
    return DEPARTMENT_TO_PERMISSIONS.get(department, ["public"])