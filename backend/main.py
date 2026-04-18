"""Move Mind AI – CLI entry point."""

from app.utils.helpers import get_logger

logger = get_logger("move-mind-ai")


def main():
    logger.info("Move Mind AI started.")
    # TODO: Wire up your chain / graph / RAG pipeline here
    #   from app.chains.base import build_simple_chain
    #   from app.graphs.agent import build_agent_graph
    #   from app.rag.chain import build_rag_chain


if __name__ == "__main__":
    main()
