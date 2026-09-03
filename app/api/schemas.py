from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    permissions: list[str] | None = None  # wired to real auth in Phase 4
    top_k: int = 5


class SourceOut(BaseModel):
    source: str
    doc_id: str
    rerank_score: float