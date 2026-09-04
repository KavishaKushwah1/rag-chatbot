"""
After an exchange completes, extracts durable user facts/preferences
(name, role, team, stated preferences) from the turn and stores them as
long-term memories. Runs as a FastAPI background task — scheduled after
the streamed response finishes, so it never adds latency for the user.
Best-effort: failures here must never break the chat flow.
"""
from __future__ import annotations
import json
import logging

from google.genai import types

from app.llm.gemini_client import get_client, MODEL
from app.memory.long_term import store_memory

logger = logging.getLogger("uvicorn.error")

EXTRACTION_PROMPT = """Extract any durable facts or preferences about the USER from this
exchange that would be useful to remember in future conversations
(e.g. their name, role, team, stated preferences, recurring context).

Ignore anything that's just about the document content, not the user.
If there is nothing worth remembering, return an empty list.

Respond ONLY with a JSON array of short fact strings, nothing else. Example:
["User's name is Priya", "User works on the engineering team"]

User message: {user_message}
Assistant reply: {assistant_reply}
"""


def extract_and_store_memories(user_id: str, user_message: str, assistant_reply: str) -> None:
    try:
        client = get_client()
        prompt = EXTRACTION_PROMPT.format(user_message=user_message, assistant_reply=assistant_reply)

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.0),
        )

        text = (response.text or "").strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        facts = json.loads(text) if text else []

        for fact in facts:
            if isinstance(fact, str) and fact.strip():
                store_memory(user_id, fact.strip())

        if facts:
            logger.info(f"Stored {len(facts)} memory fact(s) for user {user_id}")

    except Exception:
        logger.exception("Memory extraction failed (non-fatal)")