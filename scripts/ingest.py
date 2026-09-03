"""
Usage: python scripts/ingest.py [--source data/sample_docs]
"""
import argparse
from app.ingestion.pipeline import run_ingestion


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="data/sample_docs", help="Directory of docs to ingest")
    args = parser.parse_args()

    result = run_ingestion(args.source)
    print(f"\nIngestion complete: {result['documents']} documents, {result['chunks']} chunks stored in Qdrant.")


if __name__ == "__main__":
    main()