"""Streamlit UI for the CMS3 log-debugging assistant."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

from app.graphs.agent import build_rag_graph
from app.graphs.constants import (
    NODE_CLASSIFY_ISSUE,
    NODE_CLASSIFY_QUESTION,
    NODE_GENERATE_ANSWER,
    NODE_RERANK_DOCS,
    NODE_RESOLVE_CONTEXT,
    NODE_RETRIEVE_DOCS,
    NODE_REWRITE_QUESTION,
)
from app.utils.helpers import get_logger

logger = get_logger(__name__)

STATUS_LABELS = {
    NODE_CLASSIFY_QUESTION: "Classifying query...",
    NODE_REWRITE_QUESTION: "Rewriting follow-up...",
    NODE_RESOLVE_CONTEXT: "Resolving context...",
    NODE_RETRIEVE_DOCS: "Retrieving evidence...",
    NODE_RERANK_DOCS: "Reranking evidence...",
    NODE_GENERATE_ANSWER: "Generating explanation...",
    NODE_CLASSIFY_ISSUE: "Classifying issue type...",
}

_ISSUE_BADGE = {
    "bug": ("🔴 Bug", "error"),
    "business_condition": ("🟡 Business Condition", "warning"),
    "unknown": ("⚪ Unknown", "info"),
}

st.set_page_config(
    page_title="Move Mind AI",
    page_icon="M",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "graph" not in st.session_state:
    with st.spinner("Loading CMS3 debugging graph..."):
        st.session_state.graph = build_rag_graph()

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

if "last_counts" not in st.session_state:
    st.session_state.last_counts = {"retrieved": 0, "reranked": 0}

if "last_classification" not in st.session_state:
    st.session_state.last_classification = None


def reset_chat() -> None:
    """Reset chat state and allocate a new memory thread."""
    st.session_state.messages = []
    st.session_state.last_sources = []
    st.session_state.last_counts = {"retrieved": 0, "reranked": 0}
    st.session_state.last_classification = None
    st.session_state.thread_id = str(uuid.uuid4())


with st.sidebar:
    st.title("Move Mind AI")
    st.caption("Manager investigation assistant")
    st.code(st.session_state.thread_id, language=None)

    if st.button("New investigation", use_container_width=True):
        reset_chat()
        st.rerun()

    # Issue classification result
    st.divider()
    st.markdown("**Issue Classification**")
    clf = st.session_state.last_classification
    if clf and clf.get("issue_type"):
        label, kind = _ISSUE_BADGE.get(clf["issue_type"], ("⚪ Unknown", "info"))
        st.markdown(f"### {label}")
        confidence = clf.get("issue_confidence")
        if confidence is not None:
            st.progress(confidence, text=f"Confidence: {int(confidence * 100)}%")
        reason = clf.get("issue_classification_reason", "")
        if reason:
            st.caption(reason)
    else:
        st.info("Ask about an issue to see classification.")

    st.divider()
    st.markdown("**Retrieval stats**")
    st.write(f"Retrieved: {st.session_state.last_counts['retrieved']}")
    st.write(f"Reranked: {st.session_state.last_counts['reranked']}")

    st.divider()
    st.markdown("**Evidence used**")
    if st.session_state.last_sources:
        for index, document in enumerate(st.session_state.last_sources, start=1):
            metadata = document.get("metadata", {})
            label = (
                f"[{index}] {metadata.get('chunk_type', '?')} | "
                f"CID {metadata.get('customer_id', '?')} | "
                f"{metadata.get('page_path', '?')}"
            )
            with st.expander(label, expanded=False):
                st.caption(
                    " | ".join(
                        filter(
                            None,
                            [
                                f"execution={metadata.get('execution_id')}",
                                f"action={metadata.get('action')}",
                                f"step={metadata.get('step_order')}",
                                f"status={metadata.get('status')}",
                            ],
                        )
                    )
                )
                st.markdown(document.get("page_content", "")[:1000])
    else:
        st.info("Ask a CMS3 question to inspect evidence.")


st.title("Move Mind AI")
st.caption("Ask about CMS3 journeys, routes, conditions, and failure evidence.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Ask about a CID, route transition, or failure..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status = st.status("Starting...", expanded=True)
        answer_placeholder = st.empty()
        graph = st.session_state.graph
        config = {"configurable": {"thread_id": st.session_state.thread_id}}

        retrieved_documents = []
        reranked_documents = []
        answer = ""
        classification = {}

        for event in graph.stream(
            {"question": prompt, "original_question": prompt},
            config=config,
        ):
            for node_name, output in event.items():
                if node_name in STATUS_LABELS:
                    status.write(STATUS_LABELS[node_name])

                if node_name == NODE_RETRIEVE_DOCS:
                    retrieved_documents = output.get("documents", [])
                    status.write(f"Retrieved {len(retrieved_documents)} candidate chunks")

                elif node_name == NODE_RERANK_DOCS:
                    reranked_documents = output.get("reranked_documents", [])
                    status.write(f"Kept {len(reranked_documents)} reranked chunks")

                elif node_name == NODE_GENERATE_ANSWER:
                    answer = output.get("answer", "")

                elif node_name == NODE_CLASSIFY_ISSUE:
                    classification = {
                        "issue_type": output.get("issue_type"),
                        "issue_confidence": output.get("issue_confidence"),
                        "issue_classification_reason": output.get("issue_classification_reason"),
                    }

        status.update(label="Done", state="complete", expanded=False)
        answer_placeholder.markdown(answer)

        # Show classification inline below the answer
        if classification.get("issue_type"):
            label, _ = _ISSUE_BADGE.get(classification["issue_type"], ("⚪ Unknown", "info"))
            confidence = classification.get("issue_confidence", 0)
            reason = classification.get("issue_classification_reason", "")
            st.markdown(
                f"---\n**Classification:** {label} &nbsp;·&nbsp; "
                f"**Confidence:** {int(confidence * 100)}%  \n"
                f"*{reason}*"
            )

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.last_sources = reranked_documents or retrieved_documents
    st.session_state.last_counts = {
        "retrieved": len(retrieved_documents),
        "reranked": len(reranked_documents),
    }
    st.session_state.last_classification = classification
    st.rerun()
