"""Retriever factory – load a persisted vector store and return a retriever."""

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_retriever(top_k: int | None = None):
    """Load the FAISS index from disk and return a LangChain retriever."""
    vectorstore_path = PROJECT_ROOT / settings.VECTORSTORE_PATH
    embeddings = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model=settings.EMBEDDING_MODEL_NAME,
    )
    vectorstore = FAISS.load_local(
        str(vectorstore_path),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vectorstore.as_retriever(
        search_kwargs={"k": top_k or settings.RETRIEVER_TOP_K}
    )
