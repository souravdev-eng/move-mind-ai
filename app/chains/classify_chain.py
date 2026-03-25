from langchain_core.output_parsers import StrOutputParser

from app.prompts.templates import CLASSIFY_PROMPT
from app.utils.helpers import get_llm


def get_classify_chain():
    return CLASSIFY_PROMPT | get_llm("fast") | StrOutputParser()
