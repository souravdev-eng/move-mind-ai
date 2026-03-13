"""Example LangGraph agent skeleton.

Usage:
    from app.graphs.agent import build_agent_graph
"""

from typing import Annotated, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

from app.config import settings


# ── State ────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """State schema passed through the graph."""

    messages: Annotated[list, add_messages]


# ── Nodes ────────────────────────────────────────────────────────────────────

def call_model(state: AgentState) -> dict:
    """Invoke the LLM with the current message history."""
    llm = ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        temperature=settings.LLM_TEMPERATURE,
    )
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


# ── Graph ────────────────────────────────────────────────────────────────────

def build_agent_graph() -> StateGraph:
    """Construct and compile a minimal agent graph."""
    graph = StateGraph(AgentState)

    graph.add_node("agent", call_model)

    graph.set_entry_point("agent")
    graph.add_edge("agent", END)

    return graph.compile()
