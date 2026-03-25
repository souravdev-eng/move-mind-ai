"""LangGraph RAG agent with query classification and rewriting.

Usage:
    from app.graphs.agent import build_rag_graph
    graph = build_rag_graph()
    result = graph.invoke({"question": "How is state management handled?"})
    # result["answer"], result["documents"]

Graph:
    START → classify_question → [retrieve] → retrieve_docs → generate_answer → END
                              → [rewrite]  → rewrite_question → retrieve_docs → generate_answer → END
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.graphs.constants import (NODE_CLASSIFY_QUESTION, NODE_GENERATE_ANSWER,
                                  NODE_RETRIEVE_DOCS, NODE_REWRITE_QUESTION)
from app.graphs.nodes.classify_question import classify_question
from app.graphs.nodes.generate_answer import generate_answer
from app.graphs.nodes.retrieve_docs import retrieve_docs
from app.graphs.nodes.rewrite_question import rewrite_question
from app.graphs.state import GraphState
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def route_after_classify(state: GraphState) -> str:
    """Route to retrieve or rewrite based on query type."""
    logger.info(f"Routing after classify: {state['query_type']}")
    return state["query_type"]


def build_rag_graph():
    """Construct and compile the RAG graph.

    Flow: START → retrieve_docs → generate_answer → END
    """
    memory = MemorySaver()
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node(NODE_RETRIEVE_DOCS, retrieve_docs)
    workflow.add_node(NODE_GENERATE_ANSWER, generate_answer)
    workflow.add_node(NODE_CLASSIFY_QUESTION, classify_question)
    workflow.add_node(NODE_REWRITE_QUESTION, rewrite_question)

    # Wire edges
    workflow.set_entry_point(NODE_CLASSIFY_QUESTION)
    workflow.add_conditional_edges(
        NODE_CLASSIFY_QUESTION,
        route_after_classify,
        {
            "retrieve": NODE_RETRIEVE_DOCS,
            "rewrite": NODE_REWRITE_QUESTION,
        },
    )
    workflow.add_edge(NODE_RETRIEVE_DOCS, NODE_GENERATE_ANSWER)
    workflow.add_edge(NODE_REWRITE_QUESTION, NODE_RETRIEVE_DOCS)
    workflow.add_edge(NODE_GENERATE_ANSWER, END)

    return workflow.compile(checkpointer=memory)
