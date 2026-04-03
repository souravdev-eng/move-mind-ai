"""Answer chain for the CMS3 debugging assistant."""

from langchain_core.output_parsers import StrOutputParser

from app.prompts.templates import ANSWER_PROMPT
from app.utils.helpers import get_llm, question_needs_reasoning


def get_answer_chain(question: str | None = None):
    """Return the answer chain with a model preset chosen by query type."""
    model_preset = "thinking" if question and question_needs_reasoning(question) else "smart"
    return ANSWER_PROMPT | get_llm(model_preset, streaming=True) | StrOutputParser()
