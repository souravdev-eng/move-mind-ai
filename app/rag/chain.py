"""RAG chain – retrieval-augmented generation pipeline.

Usage:
    from app.rag.chain import build_rag_chain
    chain = build_rag_chain()
    answer = chain.invoke({"question": "What is …?"})
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from app.config import settings
from app.prompts.templates import RAG_PROMPT
from app.rag.retriever import get_retriever


def format_docs(docs) -> str:
    """Join retrieved document page_content into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain():
    """Build a standard retrieve → prompt → llm → parse chain."""
    retriever = get_retriever()
    llm = ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        temperature=settings.LLM_TEMPERATURE,
    )

    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
