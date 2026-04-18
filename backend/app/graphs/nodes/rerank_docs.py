"""Node: rerank_docs - rerank retrieved CMS3 evidence with FlashRank."""

from langsmith import traceable

from app.chains.reranker_chain import get_reranker
from app.config import settings
from app.graphs.state import GraphState
from app.obs.tracing import attach_span_metadata
from app.utils.helpers import dict_to_doc, doc_to_dict, get_logger

logger = get_logger(__name__)


@traceable(run_type="retriever")
def rerank_docs(state: GraphState) -> dict:
    """Rerank retrieved chunks and keep the highest-signal evidence."""
    input_documents = state.get("documents", [])
    if any(
        item.get("metadata", {}).get("chunk_type") == "api_timeline_summary"
        for item in input_documents
    ):
        logger.info("[rerank] structured API timeline query, preserving ordered context")
        attach_span_metadata(
            {
                "num_input": len(input_documents),
                "num_kept": len(input_documents),
                "cutoff": settings.RERANK_TOP_N,
                "bypass_reason": "api_timeline_summary",
            }
        )
        return {"reranked_documents": input_documents}

    documents = [dict_to_doc(item) for item in input_documents]
    if not documents:
        logger.info("[rerank] no candidates, skipping rerank")
        attach_span_metadata(
            {"num_input": 0, "num_kept": 0, "cutoff": settings.RERANK_TOP_N}
        )
        return {"reranked_documents": []}

    reranked = get_reranker().compress_documents(documents, state["question"])
    reranked_documents = [doc_to_dict(document) for document in reranked]
    logger.info("[rerank] %d -> %d chunks", len(documents), len(reranked_documents))
    attach_span_metadata(
        {
            "num_input": len(documents),
            "num_kept": len(reranked_documents),
            "cutoff": settings.RERANK_TOP_N,
        }
    )
    return {"reranked_documents": reranked_documents}
