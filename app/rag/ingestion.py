"""Document loading, splitting, and vector store creation.

Usage:
    python -m app.rag.ingestion          # ingest docs from data/raw/
    from app.rag.ingestion import ingest
"""

from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.config import settings


def load_documents(source_dir: str = "data/raw") -> list:
    """Load all supported documents from *source_dir*."""
    loader = DirectoryLoader(
        source_dir,
        glob="**/*.*",
        loader_cls=TextLoader,
        show_progress=True,
    )
    return loader.load()


def split_documents(docs: list) -> list:
    """Split documents into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    return splitter.split_documents(docs)


def create_vectorstore(chunks: list) -> FAISS:
    """Embed chunks and persist a FAISS vector store."""
    embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(settings.VECTORSTORE_PATH)
    return vectorstore


def ingest(source_dir: str = "data/raw") -> FAISS:
    """End-to-end ingestion: load → split → embed → persist."""
    docs = load_documents(source_dir)
    chunks = split_documents(docs)
    return create_vectorstore(chunks)


if __name__ == "__main__":
    ingest()
