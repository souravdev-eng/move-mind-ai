"""Question rewriting chain for follow-up CMS3 debugging queries."""

from langchain_core.output_parsers import StrOutputParser

from app.prompts.templates import QUERY_REWRITE_PROMPT
from app.utils.helpers import get_llm


def get_query_rewrite_chain():
    """Return the lightweight rewrite chain."""
    return QUERY_REWRITE_PROMPT | get_llm("fast") | StrOutputParser()
