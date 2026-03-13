"""Example tool: web search stub.

Replace with a real implementation (Tavily, SerpAPI, etc.) as needed.
"""

from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for the given query and return results."""
    # TODO: Integrate a real search provider
    return f"[stub] No results for: {query}"
