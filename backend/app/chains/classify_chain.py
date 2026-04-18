"""Classification chain for retrieve-vs-rewrite decisions."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.utils.helpers import get_llm

_CLASSIFIER_PROMPT = """\
You are a query classifier for a CMS3 log-debugging assistant.

<task>
Decide whether the user's question is:
- A standalone question that can be answered directly → respond: retrieve
- A follow-up that references a prior turn and needs context → respond: rewrite
</task>

<signals_for_rewrite>
- Uses vague references: "there", "it", "that", "that page", "that route", "next", "previous"
- Does not repeat a Customer ID (CID) or page path that was mentioned earlier
- Is a very short question (e.g. "why?" or "what about the route?") without full context
</signals_for_rewrite>

<output>
Respond with ONLY one word — either: retrieve  or  rewrite
Do not explain your answer.
</output>
"""

CLASSIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _CLASSIFIER_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{question}"),
    ]
)

def get_classify_chain():
    """Return the fast classifier chain."""
    return CLASSIFY_PROMPT | get_llm("fast") | StrOutputParser()
