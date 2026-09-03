"""
Orchestrates the full ingestion flow: load -> chunk -> embed (dense+sparse) -> store.
"""
from __future__ import annotations
from tqdm import tqdm

from app.ingestion.loaders import load_directory
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_texts_dense, embed_texts_sparse
from app.ingestion.vector_store import get_client, recreate_collection, upsert_chunks


def run_ingestion(source_dir: str, fresh: bool = True) -> dict:
    documents = load_directory(source_dir)
    if not documents:
        raise ValueError(f"No supported documents found in {source_dir}")

    all_chunks = []
    for doc in documents:
        all_chunks.extend(
            chunk_text(doc.text, doc_id=doc.doc_id, source=doc.source, permission=doc.permission)
        )

    print(f"Loaded {len(documents)} documents -> {len(all_chunks)} chunks")

    client = get_client()
    if fresh:
        recreate_collection(client)

    batch_size = 32
    for i in tqdm(range(0, len(all_chunks), batch_size), desc="Embedding + storing"):
        batch = all_chunks[i : i + batch_size]
        texts = [c.text for c in batch]
        dense_vectors = embed_texts_dense(texts)
        sparse_vectors = embed_texts_sparse(texts)
        upsert_chunks(client, list(zip(batch, dense_vectors, sparse_vectors)))

    return {"documents": len(documents), "chunks": len(all_chunks)}