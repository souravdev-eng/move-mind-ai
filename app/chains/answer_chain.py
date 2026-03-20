"""Answer chain — LLM + ANSWER_PROMPT + StrOutputParser.

Given a question and context string, generates the final answer.
"""

from langchain_core.output_parsers import StrOutputParser

from app.prompts.templates import ANSWER_PROMPT
from app.utils.helpers import get_llm

_chain = None


def get_answer_chain():
    """Return a singleton answer chain: ANSWER_PROMPT | LLM | StrOutputParser."""
    global _chain
    if _chain is None:
        _chain = ANSWER_PROMPT | get_llm() | StrOutputParser()
    return _chain
