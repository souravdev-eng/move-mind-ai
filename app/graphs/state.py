"""Shared graph state schema used by all nodes.

Extends MessagesState so the graph supports conversational chat history
(messages field with add_messages reducer) alongside RAG-specific fields.
"""

import operator
from typing import Annotated

from langchain_core.documents import Document
from langgraph.graph import MessagesState


class GraphState(MessagesState):
    """State that flows through the RAG graph.

    Inherited from MessagesState:
        messages: Annotated[list[BaseMessage], add_messages]  — chat history

    RAG-specific fields:
    """

    question: str
    query_type: str
    documents: Annotated[list[Document], operator.add]
    answer: str
