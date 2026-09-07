"""
POST /attachments/extract — extracts text from an uploaded file for use
as ephemeral, per-message context in the next /chat request. Nothing is
persisted to disk or to Qdrant here.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.auth.dependencies import get_current_user, CurrentUser
from app.attachments.extractor import extract_text, AttachmentError

router = APIRouter()


@router.post("/attachments/extract")
async def extract_attachment(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
):
    file_bytes = await file.read()
    try:
        result = extract_text(file.filename, file_bytes)
    except AttachmentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result