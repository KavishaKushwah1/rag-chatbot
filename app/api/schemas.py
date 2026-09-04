from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    session_id: str | None = None  # if omitted, server creates a new session


class SourceOut(BaseModel):
    source: str
    doc_id: str
    rerank_score: float