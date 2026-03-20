"""Router chain — LLM + ROUTER_PROMPT + StrOutputParser.

Given a question and a list of available retrievers, returns the retriever name to use.
"""

from langchain_core.output_parsers import StrOutputParser

from app.prompts.templates import ROUTER_PROMPT
from app.utils.helpers import get_llm


def get_router_chain():
    """Return a singleton router chain: ROUTER_PROMPT | LLM | StrOutputParser."""
    return ROUTER_PROMPT | get_llm() | StrOutputParser()
