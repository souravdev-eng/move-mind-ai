"""Shared LangGraph state for the CMS3 debugging assistant."""

from langgraph.graph import MessagesState


class GraphState(MessagesState):
    """State that flows through the CMS3 debugging graph."""

    original_question: str
    question: str
    query_type: str
    active_customer_id: str | None
    active_execution_id: str | None
    active_page_path: str | None
    analysis_mode: str | None
    api_view: str | None
    requested_api_count: int | None
    documents: list[dict]
    reranked_documents: list[dict]
    answer: str
