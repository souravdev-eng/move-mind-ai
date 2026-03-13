"""Retriever factory – load a persisted vector store and return a retriever."""

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.config import settings


def get_retriever(top_k: int | None = None):
    """Load the FAISS index from disk and return a LangChain retriever."""
    embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.load_local(
        settings.VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vectorstore.as_retriever(
        search_kwargs={"k": top_k or settings.RETRIEVER_TOP_K}
    )
