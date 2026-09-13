"""
Once at least 5 downvoted messages exist, summarizes the common failure
patterns across them using the LLM, so an admin sees "users are
struggling to find X" instead of a raw list of bad answers. The summary
is cached and only regenerated when the downvote count actually changes,
so we don't re-call the LLM on every panel open.
"""
from __future__ import annotations

from google.genai import types

from app.llm.gemini_client import get_client, MODEL
from app.auth.supabase_client import get_service_client

MIN_DOWNVOTES_FOR_SUMMARY = 5

SUMMARY_PROMPT = """The following are assistant replies that users marked as unhelpful
(thumbs down) in a company knowledge-base chatbot. Identify the 2-4 most
common patterns or gaps causing dissatisfaction (e.g. "missing detail on X",
"confusing wording", "topic not in the knowledge base"). Be concise and
specific. Respond as a short bulleted list, nothing else.

Downvoted replies:
{replies}
"""


def get_or_refresh_feedback_summary() -> dict:
    client = get_service_client()

    down_feedback = client.table("message_feedback").select("message_id").eq("rating", "down").execute()
    down_ids = [f["message_id"] for f in (down_feedback.data or [])]
    down_count = len(down_ids)

    if down_count < MIN_DOWNVOTES_FOR_SUMMARY:
        return {"summary": None, "based_on_count": down_count, "ready": False}

    existing = client.table("feedback_insights").select("*").eq("id", 1).single().execute()
    cached = existing.data or {}

    if cached.get("based_on_count") == down_count and cached.get("summary"):
        return {"summary": cached["summary"], "based_on_count": down_count, "ready": True}

    messages = client.table("chat_messages").select("content").in_("id", down_ids).limit(30).execute()
    replies_text = "\n\n".join(f"- {m['content']}" for m in (messages.data or []))

    gemini = get_client()
    response = gemini.models.generate_content(
        model=MODEL,
        contents=SUMMARY_PROMPT.format(replies=replies_text),
        config=types.GenerateContentConfig(temperature=0.2),
    )
    summary = (response.text or "").strip() or "Could not generate a summary."

    client.table("feedback_insights").upsert(
        {"id": 1, "summary": summary, "based_on_count": down_count}
    ).execute()

    return {"summary": summary, "based_on_count": down_count, "ready": True}