"""
POST /chat — retrieves context, streams the LLM's grounded answer as
Server-Sent Events. Sources are sent as the first event so the frontend
can render citations before/alongside the streamed tokens.
"""
from __future__ import annotations
import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.api.schemas import ChatRequest
from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.prompt_builder import build_messages
from app.llm.gemini_client import stream_completion

router = APIRouter()

MIN_RELEVANCE_SCORE = -2.0  # cross-encoder logit threshold; tuned in Phase 6


@router.post("/chat")
async def chat(request: ChatRequest):
    async def event_generator():
        results = hybrid_search(
            query=request.query,
            top_k_final=request.top_k,
            permission_filter=request.permissions,
        )

        # Low-confidence gate: if nothing cleared the bar, don't even call the LLM
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

    return EventSourceResponse(event_generator())