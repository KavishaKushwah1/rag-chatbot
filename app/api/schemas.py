from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    # permissions removed — now derived server-side from the authenticated user


class SourceOut(BaseModel):
    source: str
    doc_id: str
    rerank_score: float