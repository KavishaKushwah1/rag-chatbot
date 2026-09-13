"""
Loads raw text out of PDFs, DOCX, and Markdown/TXT files.
Every loader returns the same shape: (text, source_metadata).
"""
from __future__ import annotations
import os
from dataclasses import dataclass

from pypdf import PdfReader
from docx import Document as DocxDocument


@dataclass
class LoadedDocument:
    doc_id: str          # stable id, e.g. filename without extension
    source: str           # original filename
    text: str
    permission: list[str] # "public" | "hr" | "engineering" | ...


# Filename prefix -> permission tier. Checked longest-prefix-first so
# more specific prefixes win over shorter ones.
_PREFIX_PERMISSIONS = {
    "manager_": "manager",
    "hr_": "hr",
    "engineering_": "engineering",
    "public_": "public",
}


def _infer_permission(filename: str) -> list[str]:
    for prefix in sorted(_PREFIX_PERMISSIONS, key=len, reverse=True):
        if filename.startswith(prefix):
            return [_PREFIX_PERMISSIONS[prefix]]
    return ["public"]


def _load_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _load_docx(path: str) -> str:
    doc = DocxDocument(path)
    return "\n".join(p.text for p in doc.paragraphs)


def _load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


LOADERS = {
    ".pdf": _load_pdf,
    ".docx": _load_docx,
    ".md": _load_text,
    ".txt": _load_text,
}


def load_document(path: str) -> LoadedDocument:
    filename = os.path.basename(path)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in LOADERS:
        raise ValueError(f"Unsupported file type: {ext} ({filename})")

    text = LOADERS[ext](path)
    if not text.strip():
        raise ValueError(f"No extractable text in {filename}")

    doc_id = os.path.splitext(filename)[0]
    permission = _infer_permission(filename)

    return LoadedDocument(doc_id=doc_id, source=filename, text=text, permission=permission)


def load_directory(dir_path: str) -> list[LoadedDocument]:
    docs = []
    for filename in sorted(os.listdir(dir_path)):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in LOADERS:
            continue
        docs.append(load_document(os.path.join(dir_path, filename)))
    return docs