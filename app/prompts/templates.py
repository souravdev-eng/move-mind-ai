"""Reusable prompt templates for chains and agents."""

from langchain_core.prompts import ChatPromptTemplate

# ── RAG Prompt ───────────────────────────────────────────────────────────────

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Use the following context to answer the "
            "user's question. If you don't know the answer, say so.\n\n"
            "Context:\n{context}",
        ),
        ("human", "{question}"),
    ]
)

# ── Conversational Prompt ────────────────────────────────────────────────────

CONVERSATIONAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI assistant."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)
