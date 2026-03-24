"""Answer chain — LLM + ANSWER_PROMPT + StrOutputParser.

Given a question and context string, generates the final answer.
"""

from langchain_core.output_parsers import StrOutputParser

from app.prompts.templates import ANSWER_PROMPT
from app.utils.helpers import get_llm


def get_answer_chain():
    """Return a singleton answer chain: ANSWER_PROMPT | LLM | StrOutputParser."""
    return ANSWER_PROMPT | get_llm() | StrOutputParser()
