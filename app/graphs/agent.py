"""LangGraph RAG agent — route_query → retrieve_docs → generate_answer.

Usage:
    from app.graphs.agent import build_rag_graph
    graph = build_rag_graph()
    result = graph.invoke({"question": "How is state management handled?"})
    # result["answer"], result["documents"], result["retriever_name"]

Graph:
    START → route_query → retrieve_docs → generate_answer → END
"""

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from app.graphs.constants import NODE_GENERATE_ANSWER, NODE_RETRIEVE_DOCS, NODE_ROUTE_QUERY
from app.graphs.state import GraphState
from app.graphs.nodes.route_query import route_query
from app.graphs.nodes.retrieve_docs import retrieve_docs
from app.graphs.nodes.generate_answer import generate_answer


def build_rag_graph():
    """Construct and compile the RAG graph.

    Flow: START → route_query → retrieve_docs → generate_answer → END
    """
    memory = MemorySaver()
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node(NODE_ROUTE_QUERY, route_query)
    workflow.add_node(NODE_RETRIEVE_DOCS, retrieve_docs)
    workflow.add_node(NODE_GENERATE_ANSWER, generate_answer)

    # Wire edges
    workflow.set_entry_point(NODE_ROUTE_QUERY)
    workflow.add_edge(NODE_ROUTE_QUERY, NODE_RETRIEVE_DOCS)
    workflow.add_edge(NODE_RETRIEVE_DOCS, NODE_GENERATE_ANSWER)
    workflow.add_edge(NODE_GENERATE_ANSWER, END)

    return workflow.compile(checkpointer=memory)
