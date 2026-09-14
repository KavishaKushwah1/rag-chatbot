"""
One-off fix: creates the missing 'permission' payload index on an
existing Qdrant Cloud collection, without needing to drop and re-ingest
everything. Run once against any collection created before this fix.

Usage: python scripts\\create_qdrant_index.py
"""
from app.ingestion.vector_store import get_client, _ensure_permission_index

def main():
    client = get_client()
    _ensure_permission_index(client)
    print("Index on 'permission' field created (or already existed).")

if __name__ == "__main__":
    main()