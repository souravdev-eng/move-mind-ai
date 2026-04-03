"""Node: rerank_docs - rerank retrieved CMS3 evidence with FlashRank."""

from app.chains.reranker_chain import get_reranker
from app.graphs.state import GraphState
from app.utils.helpers import dict_to_doc, doc_to_dict, get_logger

logger = get_logger(__name__)


def rerank_docs(state: GraphState) -> dict:
    """Rerank retrieved chunks and keep the highest-signal evidence."""
    if any(
        item.get("metadata", {}).get("chunk_type") == "api_timeline_summary"
        for item in state.get("documents", [])
    ):
        logger.info("[rerank] structured API timeline query, preserving ordered context")
        return {"reranked_documents": state.get("documents", [])}

    documents = [dict_to_doc(item) for item in state.get("documents", [])]
    if not documents:
        logger.info("[rerank] no candidates, skipping rerank")
        return {"reranked_documents": []}

    reranked = get_reranker().compress_documents(documents, state["question"])
    reranked_documents = [doc_to_dict(document) for document in reranked]
    logger.info("[rerank] %d -> %d chunks", len(documents), len(reranked_documents))
    return {"reranked_documents": reranked_documents}
