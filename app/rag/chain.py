"""RAG chain – retrieval-augmented generation pipeline.

Usage:
    from app.rag.chain import build_rag_chain
    chain = build_rag_chain()
    result = chain.invoke("What is …?")
    # result = {"answer": "...", "source_documents": [...]}
"""

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

from app.config import settings
from app.prompts.templates import RAG_PROMPT
from app.rag.retriever import get_retriever


def format_docs(docs: list[Document]) -> str:
    """Join retrieved document page_content into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain():
    """Build a standard retrieve → prompt → llm → parse chain.

    Returns a chain that accepts a question string and returns:
        {"answer": str, "source_documents": list[Document]}
    """
    retriever = get_retriever()
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model=settings.LLM_MODEL_NAME,
        temperature=settings.LLM_TEMPERATURE,
        streaming=True,
    )

    # Sub-chain: retrieve docs and format for the prompt
    retrieve_and_format = retriever | format_docs

    # Full answer chain
    answer_chain = (
        {"context": retrieve_and_format, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    # Chain that returns both the answer and source documents
    def invoke_with_sources(question: str) -> dict:
        docs = retriever.invoke(question)
        context = format_docs(docs)
        answer = (RAG_PROMPT | llm | StrOutputParser()).invoke(
            {"context": context, "question": question}
        )
        return {"answer": answer, "source_documents": docs}

    return answer_chain, invoke_with_sources
