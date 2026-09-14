"""
POST /chat — retrieves context + memory, streams the LLM's grounded
answer as SSE, persists the exchange, and schedules background long-term
memory extraction (runs after the response completes, zero added latency).

Retrieval and generation are run via a background thread bridge
(asyncio.to_thread / iterate_in_thread) rather than called directly, so a
slow request doesn't block the event loop and stall every other
concurrent user's request — see app/llm/async_bridge.py for why this
matters and how it was verified.
"""

import asyncio
import json
import logging
import uuid

from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sse_starlette.sse import EventSourceResponse
from google.genai.errors import ClientError

from app.api.schemas import ChatRequest
from app.auth.dependencies import get_current_user, CurrentUser
from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.prompt_builder import build_messages
from app.llm.gemini_client import stream_completion
from app.llm.async_bridge import iterate_in_thread
from app.memory.short_term import ensure_session, get_recent_messages, save_message
from app.memory.long_term import retrieve_memories
from app.memory.extractor import extract_and_store_memories
from app.guardrails.input_guard import validate_query, QueryBlockedError
from app.guardrails.sanitizer import sanitize_chunks
from app.guardrails.meta_questions import match_meta_question, is_meta_instruction_request
from app.config import settings
from app.observability.langfuse_client import is_enabled, get_langfuse
from app.rate_limit import limiter

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

MIN_RELEVANCE_SCORE = settings.min_relevance_score


@router.post("/chat")
@limiter.limit("10/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(get_current_user),
):
    session_id = chat_request.session_id or str(uuid.uuid4())

    full_reply_parts: list[str] = []

    async def event_generator():
        langfuse = get_langfuse() if is_enabled() else None
        root_ctx = (
            langfuse.start_as_current_observation(
                as_type="span",
                name="chat_request",
                input=chat_request.query,
                metadata={"user_id": current_user.user_id, "session_id": session_id, "department": current_user.department},
            )
            if langfuse else None
        )
        root_span = root_ctx.__enter__() if root_ctx else None

        query = chat_request.query
        sources_payload: list[dict] = []
        is_unanswered = False
        try:
            try:
                query = validate_query(chat_request.query)
            except QueryBlockedError as e:
                yield {"event": "sources", "data": json.dumps([])}
                yield {"event": "token", "data": e.message}
                full_reply_parts.append(e.message)
                yield {"event": "done", "data": ""}
                return

            yield {"event": "session", "data": json.dumps({"session_id": session_id})}

            meta_response = match_meta_question(query)
            if meta_response is not None:
                yield {"event": "sources", "data": json.dumps([])}
                yield {"event": "token", "data": meta_response}
                full_reply_parts.append(meta_response)
                yield {"event": "done", "data": ""}
                if root_span:
                    root_span.update(output=meta_response)
                return

            if is_meta_instruction_request(query):
                # This is a request to design/write something, not a
                # question about company documents — answer directly with
                # no KB context injected, so retrieval keyword-matches
                # against security/policy docs can't leak irrelevant
                # company content into an unrelated meta-request.
                meta_messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. The user is asking you to write, "
                                   "design, or explain something general (like a prompt, system, "
                                   "or architecture) — this is NOT a question about this company's "
                                   "internal documents, so do not reference or invent any company "
                                   "policy content. Just answer the request directly and helpfully.",
                    },
                    {"role": "user", "content": query},
                ]
                yield {"event": "sources", "data": json.dumps([])}
                async for token in iterate_in_thread(stream_completion, meta_messages):
                    full_reply_parts.append(token)
                    yield {"event": "token", "data": token}
                yield {"event": "done", "data": ""}
                if root_span:
                    root_span.update(output="".join(full_reply_parts))
                return

            history = get_recent_messages(session_id)
            memories = retrieve_memories(current_user.user_id, query)

            if langfuse:
                with langfuse.start_as_current_observation(
                    as_type="span", name="retrieval", input={"query": query, "permissions": current_user.permissions}
                ) as retrieval_span:
                    debug = await asyncio.to_thread(
                        hybrid_search, query=query, top_k_final=chat_request.top_k,
                        permission_filter=current_user.permissions, return_debug=True,
                    )
                    results = debug["reranked"]
                    retrieval_span.update(
                        output={
                            "fusion_candidate_count": len(debug["fusion_candidates"]),
                            "reranked": [{"source": r["source"], "score": r["rerank_score"]} for r in results],
                        }
                    )
            else:
                results = await asyncio.to_thread(
                    hybrid_search, query=query, top_k_final=chat_request.top_k,
                    permission_filter=current_user.permissions,
                )

            strong_results = [r for r in results if r["rerank_score"] >= MIN_RELEVANCE_SCORE]
            strong_results = sanitize_chunks(strong_results)
            has_attachments = bool(chat_request.attached_context)
            logger.info(
                f"Retrieval: query={query!r} candidates={len(results)} "
                f"top_scores={[round(r['rerank_score'], 2) for r in results[:3]]} threshold={MIN_RELEVANCE_SCORE}"
            )

            if not strong_results and not history and not memories and not has_attachments:
                fallback = "I don't have enough information to answer that."
                is_unanswered = True
                yield {"event": "sources", "data": json.dumps([])}
                yield {"event": "token", "data": fallback}
                full_reply_parts.append(fallback)
                yield {"event": "done", "data": ""}
                if root_span:
                    root_span.update(output=fallback)
                return

            sources_payload = [
                {
                    "source": r["source"],
                    "doc_id": r["doc_id"],
                    "rerank_score": r["rerank_score"],
                    "snippet": r["text"][:600],
                }
                for r in strong_results
            ]
            yield {"event": "sources", "data": json.dumps(sources_payload)}
            if has_attachments:
                yield {
                    "event": "attachments",
                    "data": json.dumps([a.filename for a in chat_request.attached_context]),
                }

            messages = build_messages(
                query, strong_results, history=history, memories=memories,
                attachments=[a.dict() for a in (chat_request.attached_context or [])],
            )

            if langfuse:
                with langfuse.start_as_current_observation(
                    as_type="generation", name="generation", model="gemini-3.6-flash", input=messages
                ) as gen_span:
                    async for token in iterate_in_thread(stream_completion, messages):
                        full_reply_parts.append(token)
                        yield {"event": "token", "data": token}
                    gen_span.update(output="".join(full_reply_parts))
            else:
                async for token in iterate_in_thread(stream_completion, messages):
                    full_reply_parts.append(token)
                    yield {"event": "token", "data": token}

            yield {"event": "done", "data": ""}
            if root_span:
                root_span.update(output="".join(full_reply_parts))

        except ClientError as e:
            logger.exception("Gemini API error during chat generation")
            if "RESOURCE_EXHAUSTED" in str(e) or getattr(e, "code", None) == 429:
                friendly = "The assistant has hit its usage limit for now. Please try again in a minute."
            else:
                friendly = "The assistant is temporarily unavailable. Please try again shortly."
            yield {"event": "error", "data": json.dumps({"message": friendly})}
            if root_span:
                root_span.update(level="ERROR", status_message=str(e))

        except Exception as e:
            logger.exception("Error during chat generation")
            yield {"event": "error", "data": json.dumps({"message": "Something went wrong while generating a response. Please try again."})}
            if root_span:
                root_span.update(level="ERROR", status_message=str(e))

        finally:
            if root_ctx:
                root_ctx.__exit__(None, None, None)
            if langfuse:
                langfuse.flush()

            full_reply = "".join(full_reply_parts)
            if full_reply:
                ensure_session(session_id, current_user.user_id)
                save_message(session_id, current_user.user_id, "user", query)
                assistant_row = save_message(
                    session_id, current_user.user_id, "assistant", full_reply,
                    sources=sources_payload, unanswered=is_unanswered,
                    related_query=query if is_unanswered else None,
                )
                if assistant_row:
                    yield {"event": "message_id", "data": json.dumps({"message_id": assistant_row["id"]})}
                background_tasks.add_task(extract_and_store_memories, current_user.user_id, query, full_reply)

    return EventSourceResponse(event_generator(), background=background_tasks)