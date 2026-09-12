from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.sessions import router as sessions_router
from app.api.profile import router as profile_router
from app.api.attachments import router as attachments_router
from app.observability.langfuse_client import is_enabled, get_langfuse

app = FastAPI(title="RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(profile_router)
app.include_router(attachments_router)


@app.on_event("startup")
def warm_up_models():
    """
    Load embedding/reranker models at startup instead of lazily on the
    first real request, so nobody experiences a 60+ second 'hang' on
    cold start that looks indistinguishable from a bug.
    """
    from app.ingestion.embedder import get_dense_embedder, get_sparse_embedder
    from app.retrieval.reranker import get_reranker
    get_dense_embedder()
    get_sparse_embedder()
    get_reranker()


@app.on_event("shutdown")
def shutdown_event():
    if is_enabled():
        get_langfuse().flush()


@app.get("/health")
def health():
    return {"status": "ok"}