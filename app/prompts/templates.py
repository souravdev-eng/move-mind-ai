"""Reusable prompt templates for chains and agents.

Convention:
    _SYSTEM_*  → raw system-prompt text (editable, readable)
    *_PROMPT   → compiled ChatPromptTemplate (importable by chains)
"""

from langchain_core.prompts import ChatPromptTemplate

# ── System prompt text ───────────────────────────────────────────────────────

_SYSTEM_RAG = f"""You are a helpful assistant. Use the following context to answer the user's question. 
If you don't know the answer, say so.

Context:
{{context}}"""


_SYSTEM_ANSWER = f"""You are a senior technical assistant for the AMS Admin Tool team.

Rules:
- Answer based ONLY on the provided context. Do not use prior knowledge.
- If the context doesn't contain enough information, say "I don't have enough information in the docs to answer this" — never guess or hallucinate.
- Be specific: reference file names, component names, and technical details from the context.
- Use markdown formatting: headings, bullet points, code blocks where appropriate.
- When referencing information, cite the source in brackets, e.g. [architecture/overview.md > State Management].
- Keep answers concise but thorough — prefer structured responses over walls of text.

Context:
{{context}}"""

_SYSTEM_CONVERSATIONAL = "You are a helpful AI assistant."

_CLASSIFIER_PROMPT = """You are a query classifier. Your job is to understand the question based on the chat history and classify it as either rewrite or retrieve.

If the user is asking a follow-up question that references prior conversation, respond with: rewrite
If the user is asking a new standalone question, respond with: retrieve

Respond with ONLY the word `rewrite` or `retrieve`, nothing else."""

_REWRITE_PROMPT = """You are a question rewriter. Given the chat history and a follow-up question, rewrite it as a standalone question that is specific and detailed enough to retrieve relevant information from the knowledge base.

Respond with ONLY the rewritten question, nothing else."""

# ── Compiled templates ───────────────────────────────────────────────────────


CLASSIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _CLASSIFIER_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{question}"),
    ]
)

QUERY_REWRITE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _REWRITE_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{question}"),
    ]
)

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_RAG),
        ("human", "{question}"),
    ]
)


ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_ANSWER),
        ("placeholder", "{chat_history}"),
        ("human", "{question}"),
    ]
)

CONVERSATIONAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_CONVERSATIONAL),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)
