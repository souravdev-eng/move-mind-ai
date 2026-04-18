"""CLI script to run document ingestion.

Usage:
    python scripts/ingest.py                          # default: data/processed/cms3_log_chunks.json
    python scripts/ingest.py --source data/raw/cms3-logs.json
    python scripts/ingest.py --source data/raw/cms3-logs.json --export-processed
"""

import argparse

from app.rag.ingestion import build_vectorstore
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Ingest CMS3 logs or processed chunks into the Pinecone vector store."
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Path to raw CMS3 logs or processed chunks JSON (defaults to settings.PROCESSED_CHUNKS_PATH).",
    )
    parser.add_argument(
        "--source-format",
        choices=["auto", "raw", "processed"],
        default="auto",
        help="How to interpret the input source.",
    )
    parser.add_argument(
        "--export-processed",
        action="store_true",
        help="Export processed chunks when ingesting from raw logs.",
    )
    args = parser.parse_args()

    logger.info("Starting ingestion from %s …", args.source or "default path")
    build_vectorstore(
        source_path=args.source,
        source_format=args.source_format,
        export_processed=args.export_processed,
    )
    logger.info("Ingestion complete.")


if __name__ == "__main__":
    main()
