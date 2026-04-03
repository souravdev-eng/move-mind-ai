"""FlashRank reranker shared by the app graph and API."""

from flashrank import Ranker
from langchain_community.document_compressors import FlashrankRerank

from app.config import settings

_reranker: FlashrankRerank | None = None


def get_reranker() -> FlashrankRerank:
    """Return a cached FlashRank compressor for reranking retrieved documents."""
    global _reranker
    if _reranker is None:
        FlashrankRerank.model_rebuild(
            _types_namespace={"Ranker": Ranker},
            force=True,
        )
        _reranker = FlashrankRerank(
            client=Ranker(model_name=settings.FLASHRANK_MODEL_NAME),
            top_n=settings.RERANK_TOP_N,
        )
    return _reranker
