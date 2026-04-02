from flashrank import Ranker
from langchain_community.document_compressors import FlashrankRerank

FLASHRANK_MODEL = "ms-marco-TinyBERT-L-2-v2"


def get_reranker() -> FlashrankRerank:
    """Return a FlashRank compressor for reranking already-retrieved documents."""
    return FlashrankRerank(client=Ranker(model_name=FLASHRANK_MODEL))
