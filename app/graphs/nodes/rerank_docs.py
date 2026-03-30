from app.chains.reranker_chain import get_reranker
from app.graphs.state import GraphState
from app.utils.helpers import dict_to_doc, doc_to_dict, get_logger

logger = get_logger(__name__)


def rerank_docs(state: GraphState) -> dict:
    """Rerank retrieved documents using FlashRank."""
    compressor = get_reranker()
    doc_dicts = state.get("documents", [])

    # Convert dicts → Documents for the compressor
    docs = [dict_to_doc(d) for d in doc_dicts]
    reranked = compressor.compress_documents(docs, state["question"])

    # Convert back to dicts for state storage
    result = [doc_to_dict(d) for d in reranked]
    logger.info("[rerank] %d → %d docs", len(doc_dicts), len(result))
    return {"reranked_documents": result}
