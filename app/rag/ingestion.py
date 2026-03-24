"""Ingestion pipeline — load pre-processed chunks, embed, and persist a FAISS vector store.

Usage:
    python -m app.rag.ingestion                           # default: data/processed/chunks_enriched.json
    python -m app.rag.ingestion --source path/to/chunks.json

Pipeline (runs after the preprocessing notebook):
    data/processed/chunks_enriched.json
      → Load Document objects (page_content + enriched metadata)
      → Embed with OpenAI embeddings
      → Build FAISS index
      → Persist to data/vectorstore/
"""

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.rag.chunks_loader import load_processed_chunks
from app.utils.helpers import get_logger

logger = get_logger(__name__)

# Resolve paths relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks_enriched.json"


def build_vectorstore(chunks_path: Path | str = DEFAULT_CHUNKS_PATH) -> FAISS:
    """End-to-end ingestion: load chunks → embed → build FAISS index.

    Args:
        chunks_path: Path to the JSON file exported by the preprocessing notebook.

    Returns:
        The in-memory FAISS vector store (also persisted to disk).
    """
    chunks_path = Path(chunks_path)

    # ── 1. Load ──────────────────────────────────────────────────────────
    logger.info("Loading chunks from %s", chunks_path)
    documents = load_processed_chunks(chunks_path)
    logger.info("Loaded %d chunks", len(documents))

    # ── 2. Embed + Build Index ───────────────────────────────────────────
    logger.info("Embedding with '%s'...", settings.EMBEDDING_MODEL_NAME)
    embeddings = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY, model=settings.EMBEDDING_MODEL_NAME
    )
    vectorstore = FAISS.from_documents(documents, embeddings)
    logger.info(
        "FAISS index built — %d vectors, dimension %d",
        vectorstore.index.ntotal,
        vectorstore.index.d,
    )

    # ── 3. Persist ───────────────────────────────────────────────────────
    vectorstore_path = PROJECT_ROOT / settings.VECTORSTORE_PATH
    vectorstore_path.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(vectorstore_path))
    logger.info("Vector store saved to %s", vectorstore_path)

    return vectorstore


def verify_vectorstore() -> None:
    """Quick sanity check — load the persisted index and run a test query."""
    vectorstore_path = PROJECT_ROOT / settings.VECTORSTORE_PATH
    embeddings = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY, model=settings.EMBEDDING_MODEL_NAME
    )
    vectorstore = FAISS.load_local(
        str(vectorstore_path),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    logger.info(
        "Verification: loaded %d vectors from %s",
        vectorstore.index.ntotal,
        vectorstore_path,
    )

    # Test similarity search
    results = vectorstore.similarity_search("architecture overview", k=3)
    logger.info("Test query returned %d results:", len(results))
    for i, doc in enumerate(results):
        logger.info(
            "  [%d] %s — %s (%.80s...)",
            i,
            doc.metadata.get("doc_title", "?"),
            doc.metadata.get("section", "?"),
            doc.page_content,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Embed chunks and build FAISS vector store."
    )
    parser.add_argument(
        "--source",
        type=str,
        default=str(DEFAULT_CHUNKS_PATH),
        help="Path to the processed chunks JSON file.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run a verification query after building the index.",
    )
    args = parser.parse_args()

    build_vectorstore(args.source)

    if args.verify:
        verify_vectorstore()
