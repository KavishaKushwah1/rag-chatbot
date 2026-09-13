"""
Admin-only endpoints: manage user departments (with audit trail),
view feedback/unanswered-question analytics, and manage the knowledge
base (list/upload/delete documents in Qdrant) without touching a script.
"""
from __future__ import annotations
from collections import Counter, defaultdict

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.auth.dependencies import require_admin, CurrentUser
from app.auth.supabase_client import get_service_client
from app.attachments.extractor import extract_text, AttachmentError
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_texts_dense, embed_texts_sparse
from app.ingestion.vector_store import get_client, ensure_collection, upsert_chunks, COLLECTION_NAME
from app.analytics.feedback_insights import get_or_refresh_feedback_summary

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])


# ---------- Users ----------

class DepartmentUpdate(BaseModel):
    department: str


@router.get("/users")
def list_users(current_user: CurrentUser = Depends(require_admin)):
    client = get_service_client()
    result = client.table("profiles").select("id, email, department, display_name").execute()
    return result.data or []


@router.patch("/users/{user_id}")
def update_user_department(user_id: str, body: DepartmentUpdate, current_user: CurrentUser = Depends(require_admin)):
    valid = {"public", "hr", "engineering", "manager", "admin"}
    if body.department not in valid:
        raise HTTPException(status_code=400, detail=f"department must be one of {valid}")

    client = get_service_client()
    existing = client.table("profiles").select("department").eq("id", user_id).single().execute()
    old_department = (existing.data or {}).get("department")

    client.table("profiles").update({"department": body.department}).eq("id", user_id).execute()
    client.table("role_change_audit").insert(
        {
            "user_id": user_id,
            "changed_by": current_user.user_id,
            "old_department": old_department,
            "new_department": body.department,
        }
    ).execute()
    return {"ok": True}


@router.get("/audit-log")
def get_audit_log(current_user: CurrentUser = Depends(require_admin)):
    client = get_service_client()
    result = (
        client.table("role_change_audit")
        .select("user_id, changed_by, old_department, new_department, changed_at")
        .order("changed_at", desc=True)
        .limit(200)
        .execute()
    )
    return result.data or []


# ---------- Feedback / analytics ----------

@router.get("/feedback-summary")
def feedback_summary(current_user: CurrentUser = Depends(require_admin)):
    client = get_service_client()

    feedback = client.table("message_feedback").select("rating").execute().data or []
    counts = Counter(f["rating"] for f in feedback)

    unanswered = (
        client.table("chat_messages")
        .select("related_query, content, created_at")
        .eq("unanswered", True)
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    ).data or []
    unanswered = [
        {"question": row.get("related_query") or row["content"], "created_at": row["created_at"]}
        for row in unanswered
    ]

    insight = get_or_refresh_feedback_summary()

    return {
        "thumbs_up": counts.get("up", 0),
        "thumbs_down": counts.get("down", 0),
        "unanswered_questions": unanswered,
        "negative_feedback_summary": insight["summary"],
        "negative_feedback_count": insight["based_on_count"],
    }

# ---------- Knowledge base management ----------

@router.get("/documents")
def list_documents(current_user: CurrentUser = Depends(require_admin)):
    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):
        return []

    doc_stats: dict[str, dict] = defaultdict(lambda: {"chunk_count": 0, "permission": None, "source": None})
    offset = None
    while True:
        points, offset = client.scroll(COLLECTION_NAME, limit=200, offset=offset, with_payload=True, with_vectors=False)
        for p in points:
            doc_id = p.payload.get("doc_id", "unknown")
            doc_stats[doc_id]["chunk_count"] += 1
            doc_stats[doc_id]["permission"] = p.payload.get("permission")
            doc_stats[doc_id]["source"] = p.payload.get("source")
        if offset is None:
            break

    return [{"doc_id": k, **v} for k, v in doc_stats.items()]


@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    permissions: str = Form(...),
    current_user: CurrentUser = Depends(require_admin),
):
    valid_perms = {"public", "hr", "engineering", "manager"}
    requested = [p.strip() for p in permissions.split(",") if p.strip()]
    if not requested:
        raise HTTPException(status_code=400, detail="Select at least one department")
    invalid = set(requested) - valid_perms
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid department(s): {invalid}")

    file_bytes = await file.read()
    try:
        extracted = extract_text(file.filename, file_bytes)
    except AttachmentError as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc_id = file.filename.rsplit(".", 1)[0]
    chunks = chunk_text(extracted["text"], doc_id=doc_id, source=file.filename, permission=requested)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks produced from this document")

    dense_vectors = embed_texts_dense([c.text for c in chunks])
    sparse_vectors = embed_texts_sparse([c.text for c in chunks])

    qdrant_client = get_client()
    ensure_collection(qdrant_client)
    upsert_chunks(qdrant_client, list(zip(chunks, dense_vectors, sparse_vectors)))

    return {"ok": True, "doc_id": doc_id, "chunks_added": len(chunks), "permissions": requested}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str, current_user: CurrentUser = Depends(require_admin)):
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):
        raise HTTPException(status_code=404, detail="Knowledge base is empty")

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]),
    )
    return {"ok": True}