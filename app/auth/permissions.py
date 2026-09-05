"""
Maps a user's department to the set of document permission tiers they can
retrieve. Single source of truth for ACL.
"""
from __future__ import annotations

DEPARTMENT_TO_PERMISSIONS = {
    "public": ["public"],
    "hr": ["public", "hr"],
    "engineering": ["public", "engineering"],
    "manager": ["public", "hr", "engineering", "manager"],
    "admin": ["public", "hr", "engineering", "manager"],
}


def permissions_for_department(department: str) -> list[str]:
    return DEPARTMENT_TO_PERMISSIONS.get(department, ["public"])