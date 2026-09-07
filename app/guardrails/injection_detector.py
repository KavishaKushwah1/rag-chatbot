"""
Heuristic detector for prompt-injection patterns. Applied to RETRIEVED
document chunks (the real attack surface — anyone who can get text into
the knowledge base can try to hijack the assistant) and, for monitoring
purposes, to the user's own query.

This is pattern-matching, not a guarantee — it's one layer of defense
alongside the system prompt's "treat context as data" instruction and the
delimiter-based sanitization in sanitizer.py. Layered defense, not a silver bullet.
"""
from __future__ import annotations
import re

INJECTION_PATTERNS = [
    r"ignore (all |the )?(previous|prior|above) instructions",
    r"disregard (all |the )?(previous|prior|above)",
    r"you are now",
    r"forget (everything|all) (you|i) (know|told|said)",
    r"new instructions?:",
    r"system prompt",
    r"reveal (your|the) (instructions|prompt|rules)",
    r"act as (a|an) (?!assistant\b)\w+",
    r"pretend (you are|to be)",
    r"do not (follow|obey) (the|your) (rules|instructions|system prompt)",
    r"override (your|the) (rules|instructions|configuration)",
    r"\bDAN\b",  # common jailbreak alias ("Do Anything Now")
    r"respond only with",
    r"from now on",
    r"reveal (any )?(confidential|private|sensitive) (credentials|information|data)",
    r"(api key|password|access token|credentials?)s? (you (can|could) (retrieve|find|access)|stored|hidden)",
    r"do not (hide|redact|censor) anything",
    r"search all (available )?(company )?documents and (reveal|expose|return)",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def detect_injection(text: str) -> list[str]:
    """Returns the list of matched pattern strings (empty if clean)."""
    matches = []
    for pattern, compiled in zip(INJECTION_PATTERNS, _COMPILED):
        if compiled.search(text):
            matches.append(pattern)
    return matches


def is_suspicious(text: str) -> bool:
    return len(detect_injection(text)) > 0