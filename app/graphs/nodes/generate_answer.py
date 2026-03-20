"""Node: generate_answer — LLM generates a final answer from retrieved context."""

from app.chains.answer_chain import get_answer_chain
from app.graphs.state import GraphState
from app.utils.helpers import format_docs, get_logger

logger = get_logger(__name__)


def generate_answer(state: GraphState) -> dict:
    """Generate a final answer using retrieved context."""
    chain = get_answer_chain()
    context = format_docs(state["documents"])

    answer = chain.invoke({
        "question": state["question"],
        "context": context,
    })

    logger.info("[generate] → answer ready (%d chars)", len(answer))
    return {"answer": answer}
