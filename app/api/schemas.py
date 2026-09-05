from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    session_id: str | None = None


class SourceOut(BaseModel):
    source: str
    doc_id: str
    rerank_score: float


class SessionUpdateRequest(BaseModel):
    title: str | None = None
    pinned: bool | None = None


class ProfileUpdateRequest(BaseModel):
    display_name: str