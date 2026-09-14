"""
Recognizes generic 'what can you do / who are you' style questions and
answers them directly with a canned capability description, bypassing
retrieval entirely. These aren't knowledge-base lookups, so gating them
behind document-relevance scoring produces a confusing "I don't have
enough information" as someone's very first message — a bad first
impression for an otherwise correct fallback rule.
"""
from __future__ import annotations
import re

META_PATTERNS = [
    r"^(hi|hello|hey)[\s!.,]*$",
    r"how can you help",
    r"what can you (do|help with)",
    r"who are you",
    r"what are you",
    r"what is this( (app|tool|assistant|bot))?",
    r"how does this work",
    r"what do you know",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in META_PATTERNS]

META_INSTRUCTION_PATTERNS = [
    r"write a (detailed )?prompt",
    r"design (a|an|this) system",
    r"instructs? an llm to",
    r"how would you (build|design|architect)",
    r"create a system prompt",
]

_META_INSTRUCTION_COMPILED = [re.compile(p, re.IGNORECASE) for p in META_INSTRUCTION_PATTERNS]

CAPABILITY_RESPONSE = (
    "I'm the Acme Knowledge Assistant. I can answer questions about company "
    "policies (HR, engineering, product, and compliance docs), cite the exact "
    "source for every answer, remember context across our conversation, and "
    "read documents you attach. Ask me about things like PTO, remote work, "
    "deployment procedures, pricing, or onboarding — or attach a file and ask "
    "about it directly."
)


def match_meta_question(query: str) -> str | None:
    """Returns the canned response if the query is a generic meta/greeting
    question, otherwise None."""
    stripped = query.strip()
    for compiled in _COMPILED:
        if compiled.search(stripped):
            return CAPABILITY_RESPONSE
    return None


def is_meta_instruction_request(query: str) -> bool:
    """True if the query asks the assistant to design/write a system or prompt,
    rather than asking a question about company content."""
    return any(compiled.search(query) for compiled in _META_INSTRUCTION_COMPILED)