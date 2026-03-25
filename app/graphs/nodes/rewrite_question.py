from app.chains.query_rewrite_chain import get_query_rewrite_chain
from app.graphs.state import GraphState
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def rewrite_question(state: GraphState):
    logger.info(f"Rewriting question: {state['question']}")

    question = state["question"]
    chain = get_query_rewrite_chain()
    result = chain.invoke({"question": question, "chat_history": state.get("messages", [])})

    logger.info(f"Rewritten question: {result}")

    return {"question": result}
