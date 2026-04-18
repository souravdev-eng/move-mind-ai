"""Node: route_query — LLM picks the right retriever for the question."""

from app.chains.router_chain import get_router_chain
from app.graphs.state import GraphState
from app.rag.retriever_registry import get_retriever_registry
from app.utils.helpers import get_logger

logger = get_logger(__name__)

DEFAULT_RETRIEVER = "admin_tech_docs"


def route_query(state: GraphState) -> dict:
    """LLM decides which retriever to use based on the question."""
    registry = get_retriever_registry()
    chain = get_router_chain()

    retriever_list = "\n".join(
        f"- {name}: {info['description']}" for name, info in registry.items()
    )

    chosen = chain.invoke(
        {
            "question": state["question"],
            "retriever_list": retriever_list,
        }
    ).strip()

    # Fallback if LLM returns something unexpected
    if chosen not in registry:
        chosen = DEFAULT_RETRIEVER

    logger.info("[router] → %s", chosen)
    return {"retriever_name": chosen}
