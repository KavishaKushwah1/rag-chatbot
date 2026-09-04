"""
POST /chat — retrieves context + memory, streams the LLM's grounded
answer as SSE, persists the exchange, and schedules background long-term
memory extraction (runs after the response completes, zero added latency).
"""
from __future__ import annotations
import json
import logging
import uuid

from fastapi import APIRouter, Depends, BackgroundTasks
from sse_starlette.sse import EventSourceResponse

from app.api.schemas import ChatRequest
from app.auth.dependencies import get_current_user, CurrentUser
from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.prompt_builder import build_messages
from app.llm.gemini_client import stream_completion
from app.memory.short_term import ensure_session, get_recent_messages, save_message
from app.memory.long_term import retrieve_memories
from app.memory.extractor import extract_and_store_memories

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

MIN_RELEVANCE_SCORE = -2.0


@router.post("/chat")
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(get_current_user),
):
    session_id = request.session_id or str(uuid.uuid4())
    ensure_session(session_id, current_user.user_id)

    full_reply_parts: list[str] = []

    async def event_generator():
        try:
            yield {"event": "session", "data": json.dumps({"session_id": session_id})}

            history = get_recent_messages(session_id)
            memories = retrieve_memories(current_user.user_id, request.query)

            results = hybrid_search(
                query=request.query,
                top_k_final=request.top_k,
                permission_filter=current_user.permissions,
            )
            strong_results = [r for r in results if r["rerank_score"] >= MIN_RELEVANCE_SCORE]

            # Only give up entirely if there's no KB match AND no conversational
            # context (history/memory) to fall back on. A memory-only question
            # like "what's my name?" has no KB match but should still be answered.
            if not strong_results and not history and not memories:
                fallback = "I don't have enough information to answer that."
                yield {"event": "sources", "data": json.dumps([])}
                yield {"event": "token", "data": fallback}
                full_reply_parts.append(fallback)
                yield {"event": "done", "data": ""}
                return

            sources_payload = [
                {"source": r["source"], "doc_id": r["doc_id"], "rerank_score": r["rerank_score"]}
                for r in strong_results
            ]
            yield {"event": "sources", "data": json.dumps(sources_payload)}

            messages = build_messages(request.query, strong_results, history=history, memories=memories)

            for token in stream_completion(messages):
                full_reply_parts.append(token)
                yield {"event": "token", "data": token}

            yield {"event": "done", "data": ""}

        except Exception as e:
            logger.exception("Error during chat generation")
            yield {"event": "error", "data": json.dumps({"message": str(e)})}

        finally:
            full_reply = "".join(full_reply_parts)
            if full_reply:
                save_message(session_id, current_user.user_id, "user", request.query)
                save_message(session_id, current_user.user_id, "assistant", full_reply)
                background_tasks.add_task(
                    extract_and_store_memories, current_user.user_id, request.query, full_reply
                )

    return EventSourceResponse(event_generator(), background=background_tasks)