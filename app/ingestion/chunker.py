"""
Splits document text into overlapping chunks on sentence/paragraph
boundaries — never mid-sentence, which is what naive fixed-char-length
chunking gets wrong and hurts retrieval precision.
"""
from __future__ import annotations
import re
from dataclasses import dataclass

from app.config import settings

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    source: str
    permission: str
    chunk_index: int
    text: str


def _split_sentences(text: str) -> list[str]:
    # Split on paragraphs first (preserves markdown headers as their own unit),
    # then sentences within each paragraph.
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    sentences = []
    for para in paragraphs:
        sentences.extend(s.strip() for s in _SENTENCE_SPLIT_RE.split(para) if s.strip())
    return sentences


def chunk_text(
    text: str,
    doc_id: str,
    source: str,
    permission: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Chunk]:
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    sentences = _split_sentences(text)
    chunks: list[Chunk] = []
    current: list[str] = []
    current_len = 0
    chunk_index = 0

    def flush():
        nonlocal current, current_len, chunk_index
        if not current:
            return
        chunk_text_str = " ".join(current)
        chunks.append(
            Chunk(
                chunk_id=f"{doc_id}::{chunk_index}",
                doc_id=doc_id,
                source=source,
                permission=permission,
                chunk_index=chunk_index,
                text=chunk_text_str,
            )
        )
        chunk_index += 1

    for sentence in sentences:
        sentence_len = len(sentence)

        if current_len + sentence_len > chunk_size and current:
            flush()
            # carry overlap: keep trailing sentences whose combined length <= overlap
            overlap_sentences = []
            overlap_len = 0
            for s in reversed(current):
                if overlap_len + len(s) > chunk_overlap:
                    break
                overlap_sentences.insert(0, s)
                overlap_len += len(s)
            current = overlap_sentences
            current_len = overlap_len

        current.append(sentence)
        current_len += sentence_len

    flush()
    return chunks