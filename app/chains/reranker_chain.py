from langchain_community.document_compressors import FlashrankRerank


def get_reranker() -> FlashrankRerank:
    """Return a FlashRank compressor for reranking already-retrieved documents."""
    return FlashrankRerank(model="ms-marco-MiniLM-L-12-v2")
