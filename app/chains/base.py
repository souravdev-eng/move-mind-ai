"""Base / example chain definitions.

Usage:
    from app.chains.base import build_simple_chain
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import settings


def build_simple_chain():
    """Return a minimal prompt | llm | parser chain."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            ("human", "{input}"),
        ]
    )
    llm = ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        temperature=settings.LLM_TEMPERATURE,
    )
    return prompt | llm | StrOutputParser()
