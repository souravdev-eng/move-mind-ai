from app.chains.classify_chain import get_classify_chain
from app.graphs.state import GraphState
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def classify_question(state: GraphState):
    logger.info(f"Classifying question: {state['question']}")

    question = state["question"]
    chain = get_classify_chain()
    result = chain.invoke({"question": question, "chat_history": state.get("messages", [])})

    logger.info(f"Classification result: {result}")

    return {"query_type": result}
