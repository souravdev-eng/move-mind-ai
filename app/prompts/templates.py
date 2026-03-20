"""Reusable prompt templates for chains and agents."""

from langchain_core.prompts import ChatPromptTemplate

# ── RAG Prompt (simple chain) ────────────────────────────────────────────────

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

# ── Router Prompt (LangGraph — route_query node) ────────────────────────────

ROUTER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a query router. Given a user question, decide which knowledge base "
            "to search. You MUST respond with ONLY the retriever name, nothing else.\n\n"
            "Available retrievers:\n"
            "{retriever_list}\n\n"
            "If the question doesn't clearly match any retriever, default to: admin_tech_docs",
        ),
        ("human", "{question}"),
    ]
)

# ── Answer Prompt (LangGraph — generate_answer node) ────────────────────────

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant for the AMS Admin Tool team. "
            "Use the following context to answer the user's question accurately and concisely. "
            "If the context doesn't contain enough information, say so — don't make things up.\n\n"
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
