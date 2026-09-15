# Acme Knowledge Assistant

A production-style Retrieval-Augmented Generation (RAG) chatbot that answers questions from a private company knowledge base — with hybrid search, role-based access control, persistent memory, and a measurable evaluation pipeline. Built to survive real deployment constraints, not just run on localhost.

**Live demo:** [rag-chatbot-ebon-xi.vercel.app](https://rag-chatbot-ebon-xi.vercel.app)

---

## Why this project

Most RAG demos stop at "embed and ask an LLM." This one is built the way a real internal tool would need to be: access-controlled at the query layer (not filtered after the fact), measured with automated evaluation rather than manual spot-checks, and resilient enough to survive concurrent users and a real deployment environment.

## Features

**Retrieval**
- Hybrid dense + sparse (BM25) search with Reciprocal Rank Fusion, reranked by a cross-encoder for precision
- Role-based access control enforced as a Qdrant metadata filter *inside* the vector query — restricted documents are never retrieved, not just hidden from the response

**Conversation**
- Short-term memory (session history) and long-term memory (per-user, persisted across logins)
- Prompt-injection and data-exfiltration guardrails, with a calibrated confidence threshold to prevent hallucinated answers
- File attachments (PDF/DOCX/TXT/MD) answered as ephemeral, sanitized context

**Admin & Ops**
- Admin panel: manage user roles (with an audit log), upload/delete knowledge-base documents, review feedback analytics
- Thumbs up/down feedback with auto-summarized insight generation once enough negative signal accumulates
- End-to-end request tracing (Langfuse) that separates retrieval failures from generation failures
- Automated evaluation pipeline (Ragas) — faithfulness, answer relevancy, context precision/recall — on a categorized golden test set

**Security**
- Every request re-verifies the caller's role from the database — never trusts a client-supplied value
- Domain-restricted signup enforced by a database trigger, not just frontend validation
- Rate limiting, locked-down CORS, and clean error messages that never leak internals

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python |
| Frontend | React, Vite, TailwindCSS |
| Vector DB | Qdrant (hybrid search + metadata filtering) |
| Embeddings / Reranking | FastEmbed (ONNX) |
| LLM | Google Gemini |
| Auth & Database | Supabase (Postgres + Auth) |
| Evaluation | Ragas |
| Observability | Langfuse |
| Deployment | Render (backend), Vercel (frontend), Qdrant Cloud |

## Architecture

```
React (Vercel)
   │  HTTPS / SSE
   ▼
FastAPI (Render)
   ├── Auth ──────────► Supabase (JWT verification, role lookup)
   ├── Retrieval ─────► Qdrant Cloud (hybrid search, ACL filter, rerank)
   ├── Generation ────► Gemini (streamed response)
   ├── Memory ────────► Supabase (short-term) + Qdrant (long-term)
   └── Tracing ───────► Langfuse
```

## Getting started

```bash
git clone https://github.com/<your-username>/rag-chatbot.git
cd rag-chatbot

python -m venv venv
venv\Scripts\activate        # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

cp .env.example .env         # fill in your API keys and Qdrant/Supabase credentials
docker compose up -d         # local Qdrant instance
python scripts/generate_sample_docs.py
python scripts/ingest.py

uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Full environment variable reference is in `.env.example` and `frontend/.env.example`.

## Evaluation

```bash
python eval/run_eval.py
```
Runs a categorized golden test set (factual / edge-case / adversarial) through the live retrieval + generation pipeline and scores it with Ragas. Reports are written to `eval/reports/`.

## Known limitations

- No knowledge-base version history — documents are replaced, not versioned
- Free-tier hosting means the backend cold-starts after inactivity
- Prompt-injection detection is pattern-based; a dedicated classifier would be more robust

## License

MIT
