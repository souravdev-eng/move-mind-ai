"""CLI script to run document ingestion.

Usage:
    python scripts/ingest.py                   # default: data/raw/
    python scripts/ingest.py --source data/raw
"""

import argparse

from app.rag.ingestion import ingest
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into the vector store.")
    parser.add_argument(
        "--source",
        type=str,
        default="data/raw",
        help="Directory containing source documents.",
    )
    args = parser.parse_args()

    logger.info("Starting ingestion from %s …", args.source)
    ingest(source_dir=args.source)
    logger.info("Ingestion complete.")


if __name__ == "__main__":
    main()
