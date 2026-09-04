"""
POST /chat — retrieves context, streams the LLM's grounded answer as
Server-Sent Events. Permission tier comes from the verified user's
department (Phase 4), never from the request body.
"""
from __future__ import annotations
import json
import logging

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from app.api.schemas import ChatRequest
from app.auth.dependencies import get_current_user, CurrentUser
from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.prompt_builder import build_messages
from app.llm.gemini_client import stream_completion

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

MIN_RELEVANCE_SCORE = -2.0


@router.post("/chat")
async def chat(request: ChatRequest, current_user: CurrentUser = Depends(get_current_user)):
    async def event_generator():
        try:
            results = hybrid_search(
                query=request.query,
                top_k_final=request.top_k,
                permission_filter=current_user.permissions,
            )

            strong_results = [r for r in results if r["rerank_score"] >= MIN_RELEVANCE_SCORE]
            if not strong_results:
                yield {"event": "sources", "data": json.dumps([])}
                yield {"event": "token", "data": "I don't have enough information to answer that."}
                yield {"event": "done", "data": ""}
                return

            sources_payload = [
                {"source": r["source"], "doc_id": r["doc_id"], "rerank_score": r["rerank_score"]}
                for r in strong_results
            ]
            yield {"event": "sources", "data": json.dumps(sources_payload)}

            messages = build_messages(request.query, strong_results)

            for token in stream_completion(messages):
                yield {"event": "token", "data": token}

            yield {"event": "done", "data": ""}

        except Exception as e:
            logger.exception("Error during chat generation")
            yield {"event": "error", "data": json.dumps({"message": str(e)})}

    return EventSourceResponse(event_generator())