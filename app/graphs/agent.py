"""LangGraph agent for the CMS3 log-debugging assistant."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.graphs.constants import (
    NODE_CLASSIFY_ISSUE,
    NODE_CLASSIFY_QUESTION,
    NODE_GENERATE_ANSWER,
    NODE_RERANK_DOCS,
    NODE_RESOLVE_CONTEXT,
    NODE_RETRIEVE_DOCS,
    NODE_REWRITE_QUESTION,
)
from app.graphs.nodes.classify_issue import classify_issue
from app.graphs.nodes.classify_question import classify_question
from app.graphs.nodes.generate_answer import generate_answer
from app.graphs.nodes.resolve_context import resolve_context
from app.graphs.nodes.rerank_docs import rerank_docs
from app.graphs.nodes.retrieve_docs import retrieve_docs
from app.graphs.nodes.rewrite_question import rewrite_question
from app.graphs.state import GraphState
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def route_after_classify(state: GraphState) -> str:
    """Route to direct retrieval or query rewriting."""
    logger.info("Routing after classify: %s", state["query_type"])
    return state["query_type"]


def build_rag_graph():
    """Construct and compile the CMS3 debugging graph with thread memory."""
    workflow = StateGraph(GraphState)
    workflow.add_node(NODE_CLASSIFY_QUESTION, classify_question)
    workflow.add_node(NODE_REWRITE_QUESTION, rewrite_question)
    workflow.add_node(NODE_RESOLVE_CONTEXT, resolve_context)
    workflow.add_node(NODE_RETRIEVE_DOCS, retrieve_docs)
    workflow.add_node(NODE_RERANK_DOCS, rerank_docs)
    workflow.add_node(NODE_GENERATE_ANSWER, generate_answer)
    workflow.add_node(NODE_CLASSIFY_ISSUE, classify_issue)

    workflow.set_entry_point(NODE_CLASSIFY_QUESTION)
    workflow.add_conditional_edges(
        NODE_CLASSIFY_QUESTION,
        route_after_classify,
        {
            "retrieve": NODE_RESOLVE_CONTEXT,
            "rewrite": NODE_REWRITE_QUESTION,
        },
    )
    workflow.add_edge(NODE_REWRITE_QUESTION, NODE_RESOLVE_CONTEXT)
    workflow.add_edge(NODE_RESOLVE_CONTEXT, NODE_RETRIEVE_DOCS)
    workflow.add_edge(NODE_RETRIEVE_DOCS, NODE_RERANK_DOCS)
    workflow.add_edge(NODE_RERANK_DOCS, NODE_GENERATE_ANSWER)
    workflow.add_edge(NODE_GENERATE_ANSWER, NODE_CLASSIFY_ISSUE)
    workflow.add_edge(NODE_CLASSIFY_ISSUE, END)

    compiled_workflow = workflow.compile(checkpointer=MemorySaver())
    compiled_workflow.get_graph().draw_mermaid_png(output_file_path="graph.png")
    return compiled_workflow
