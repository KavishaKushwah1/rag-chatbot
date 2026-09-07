"""
Thin wrapper around Gemini 2.5 Flash with streaming.
Keeps the same interface as groq_client.stream_completion() so the rest
of the app (prompt_builder, chat.py) doesn't need to change.
"""
from __future__ import annotations
from collections.abc import Iterator

from google import genai
from google.genai import types

from app.config import settings

MODEL = "gemini-3.6-flash"

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")
        _client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=30_000),  # 30s, in milliseconds
        )
    return _client


def _split_messages(messages: list[dict]) -> tuple[str | None, list[types.Content]]:
    """
    Converts OpenAI-style [{"role": "system"/"user"/"assistant", "content": str}]
    into Gemini's format: a separate system_instruction string, plus a list of
    types.Content turns (Gemini uses role "model" instead of "assistant").
    """
    system_instruction = None
    contents: list[types.Content] = []

    for msg in messages:
        if msg["role"] == "system":
            system_instruction = msg["content"]
            continue
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    return system_instruction, contents


def stream_completion(messages: list[dict], temperature: float = 0.2) -> Iterator[str]:
    """Yields text tokens as they arrive from Gemini."""
    client = get_client()
    system_instruction, contents = _split_messages(messages)

    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction,
    )

    stream = client.models.generate_content_stream(
        model=MODEL,
        contents=contents,
        config=config,
    )

    for chunk in stream:
        if chunk.text:
            yield chunk.text