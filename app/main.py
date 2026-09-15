from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.rate_limit import limiter

from app.api.chat import router as chat_router
from app.api.sessions import router as sessions_router
from app.api.profile import router as profile_router
from app.api.attachments import router as attachments_router
from app.observability.langfuse_client import is_enabled, get_langfuse
from app.api.admin import router as admin_router
from app.api.feedback import router as feedback_router

app = FastAPI(title="RAG Chatbot API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rag-chatbot-ebon-xi.vercel.app", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(profile_router)
app.include_router(attachments_router)
app.include_router(admin_router)
app.include_router(feedback_router)

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