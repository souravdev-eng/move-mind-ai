"""Node: generate_answer - synthesize a grounded CMS3 debugging answer."""

from langchain_core.messages import AIMessage, HumanMessage

from app.chains.answer_chain import get_answer_chain
from app.graphs.nodes.resolve_context import API_VIEW_NAMED, API_VIEW_TRANSPORT
from app.graphs.state import GraphState
from app.prompts.templates import CMS3_CONTEXT_SCHEMA
from app.utils.helpers import format_docs, get_logger

logger = get_logger(__name__)


def _debug_context_summary(state: GraphState) -> str:
    """Render persisted session context for the answer prompt."""
    lines = [
        f"active_customer_id: {state.get('active_customer_id') or 'unknown'}",
        f"active_execution_id: {state.get('active_execution_id') or 'unknown'}",
        f"active_page_path: {state.get('active_page_path') or 'unknown'}",
        f"analysis_mode: {state.get('analysis_mode') or 'general'}",
        f"api_view: {state.get('api_view') or 'not_set'}",
    ]
    if state.get("requested_api_count") is not None:
        lines.append(f"requested_api_count: {state['requested_api_count']}")
    return "\n".join(lines)


def _api_clarification_answer(state: GraphState, context_documents: list[dict]) -> str | None:
    """Ask for clarification when the user-provided count conflicts with API interpretation."""
    if state.get("analysis_mode") != "api_calls":
        return None

    summary_document = next(
        (
            document
            for document in context_documents
            if document.get("metadata", {}).get("chunk_type") == "api_timeline_summary"
        ),
        None,
    )
    if not summary_document:
        return None

    metadata = summary_document.get("metadata", {})
    requested_count = state.get("requested_api_count")
    api_view = state.get("api_view")
    transport_count = metadata.get("graphql_request_count")
    named_count = metadata.get("named_graphql_operation_count")

    if requested_count is None:
        return None

    if (
        api_view == API_VIEW_NAMED
        and named_count is not None
        and transport_count is not None
        and requested_count != named_count
        and requested_count == transport_count
    ):
        return (
            f"I see two valid interpretations here: there are {named_count} named `gql_*` "
            f"operations, but {transport_count} transport-level `graphql_request` events. "
            f"When you say `{requested_count} APIs`, do you want the {transport_count} "
            f"transport requests or the {named_count} named GraphQL operations?"
        )

    if (
        api_view == API_VIEW_TRANSPORT
        and named_count is not None
        and transport_count is not None
        and requested_count != transport_count
        and requested_count == named_count
    ):
        return (
            f"I see two valid interpretations here: there are {transport_count} transport-level "
            f"`graphql_request` events and {named_count} named `gql_*` operations. "
            f"When you say `{requested_count} APIs`, do you want the {named_count} named "
            "operations or the transport requests?"
        )

    return None


def generate_answer(state: GraphState) -> dict:
    """Generate the final answer from reranked CMS3 evidence and chat history."""
    context_documents = state.get("reranked_documents") or state.get("documents", [])
    clarification_answer = _api_clarification_answer(state, context_documents)
    original_question = state.get("original_question", state["question"])

    if clarification_answer:
        logger.info("[generate] clarification needed for API interpretation")
        return {
            "answer": clarification_answer,
            "messages": [
                HumanMessage(content=original_question),
                AIMessage(content=clarification_answer),
            ],
        }

    context = format_docs(context_documents)
    effective_question = state["question"]
    explanation_mode = state.get("explanation_mode") or "manager"
    chain = get_answer_chain(effective_question, explanation_mode=explanation_mode)

    invoke_kwargs = {
        "question": original_question,
        "effective_question": effective_question,
        "debug_context": _debug_context_summary(state),
        "context": context,
        "chat_history": state.get("messages", []),
    }
    # Developer prompt uses context_schema; manager prompt does not expose it
    if explanation_mode == "developer":
        invoke_kwargs["context_schema"] = CMS3_CONTEXT_SCHEMA

    answer = chain.invoke(invoke_kwargs)

    logger.info("[generate] answer ready (%d chars)", len(answer))
    return {
        "answer": answer,
        "messages": [
            HumanMessage(content=original_question),
            AIMessage(content=answer),
        ],
    }
