"""Answer chain for the CMS3 debugging assistant."""

from langchain_core.output_parsers import StrOutputParser

from app.prompts.templates import DEVELOPER_ANSWER_PROMPT, MANAGER_ANSWER_PROMPT
from app.utils.helpers import get_llm, question_needs_reasoning


def get_answer_chain(question: str | None = None, explanation_mode: str = "manager"):
    """Return the answer chain with prompt and model chosen by audience and query type.

    explanation_mode:
        "manager"   — plain English prompt for non-technical manager (default)
        "developer" — technical prompt for developer Jira ticket (Week 2)
    """
    prompt = (
        DEVELOPER_ANSWER_PROMPT
        if explanation_mode == "developer"
        else MANAGER_ANSWER_PROMPT
    )
    model_preset = (
        "thinking" if question and question_needs_reasoning(question) else "smart"
    )
    return prompt | get_llm(model_preset, streaming=True) | StrOutputParser()
