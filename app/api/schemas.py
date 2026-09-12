from pydantic import BaseModel, field_validator


class AttachedContext(BaseModel):
    filename: str
    text: str


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    session_id: str | None = None
    attached_context: list[AttachedContext] | None = None

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v


class SourceOut(BaseModel):
    source: str
    doc_id: str
    rerank_score: float


class SessionUpdateRequest(BaseModel):
    title: str | None = None
    pinned: bool | None = None


class ProfileUpdateRequest(BaseModel):
    display_name: str