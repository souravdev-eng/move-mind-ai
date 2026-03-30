"""Shared graph state schema used by all nodes.

Extends MessagesState so the graph supports conversational chat history
(messages field with add_messages reducer) alongside RAG-specific fields.
"""

import operator
from typing import Annotated

from langgraph.graph import MessagesState


class GraphState(MessagesState):
    """State that flows through the RAG graph.

    Inherited from MessagesState:
        messages: Annotated[list[BaseMessage], add_messages]  — chat history

    RAG-specific fields:
        documents / reranked_documents are stored as plain dicts
        (keys: page_content, metadata) for msgpack-safe serialization.
    """

    question: str
    query_type: str
    documents: Annotated[list[dict], operator.add]
    reranked_documents: Annotated[list[dict], operator.add]
    answer: str
