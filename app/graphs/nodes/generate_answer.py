"""Node: generate_answer — LLM generates a final answer from retrieved context."""

from langchain_core.messages import AIMessage, HumanMessage

from app.chains.answer_chain import get_answer_chain
from app.graphs.state import GraphState
from app.utils.helpers import format_docs, get_logger

logger = get_logger(__name__)


def generate_answer(state: GraphState) -> dict:
    """Generate a final answer using retrieved context and chat history."""
    chain = get_answer_chain()
    context = format_docs(state["documents"])
    chat_history = state.get("messages", [])

    answer = chain.invoke(
        {
            "question": state["question"],
            "context": context,
            "chat_history": chat_history,
        }
    )

    logger.info("[generate] → answer ready (%d chars)", len(answer))

    # Append the current turn to messages for memory
    return {
        "answer": answer,
        "messages": [
            HumanMessage(content=state["question"]),
            AIMessage(content=answer),
        ],
    }
