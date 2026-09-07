"""
Extracts text from an uploaded file's bytes (no disk write, no
permanent storage). Reuses the same libraries as the ingestion loaders
but operates on in-memory streams since this is a per-request, ephemeral
attachment — not something we're adding to the shared knowledge base.
"""
from __future__ import annotations
import io
import os

from pypdf import PdfReader
from docx import Document as DocxDocument

MAX_CHARS = 20_000  # keeps one attachment from blowing out the prompt
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


class AttachmentError(ValueError):
    pass


def extract_text(filename: str, file_bytes: bytes) -> dict:
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise AttachmentError(
            f"Unsupported file type '{ext}'. Supported: PDF, DOCX, TXT, MD."
        )
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise AttachmentError("File too large (max 10MB).")

    stream = io.BytesIO(file_bytes)

    if ext == ".pdf":
        reader = PdfReader(stream)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif ext == ".docx":
        doc = DocxDocument(stream)
        text = "\n".join(p.text for p in doc.paragraphs)
    else:  # .txt / .md
        text = file_bytes.decode("utf-8", errors="replace")

    text = text.strip()
    if not text:
        raise AttachmentError("No extractable text found in this file.")

    truncated = len(text) > MAX_CHARS
    if truncated:
        text = text[:MAX_CHARS]

    return {"filename": filename, "text": text, "truncated": truncated}