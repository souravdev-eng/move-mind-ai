"""Streamlit chat UI for the Move Mind AI RAG pipeline.

Run:
    streamlit run app/ui/streamlit_app.py

This is a temporary frontend. Delete app/ui/ when migrating to React.
"""

import asyncio
import sys
import uuid
from pathlib import Path

# Ensure project root is on sys.path so `app.*` imports work
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from app.graphs.agent import build_rag_graph
from app.graphs.constants import (
    NODE_CLASSIFY_QUESTION,
    NODE_GENERATE_ANSWER,
    NODE_RETRIEVE_DOCS,
    NODE_REWRITE_QUESTION,
)
from app.utils.helpers import get_logger

logger = get_logger(__name__)

_STATUS_LABELS = {
    NODE_CLASSIFY_QUESTION: "🔀 Classifying query...",
    NODE_REWRITE_QUESTION: "✏️ Rewriting question...",
    NODE_RETRIEVE_DOCS: "🔍 Retrieving documents...",
    NODE_GENERATE_ANSWER: "💡 Generating answer...",
}


# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Move Mind AI",
    page_icon="🧠",
    layout="wide",
)


# ── Session state init ───────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "graph" not in st.session_state:
    with st.spinner("Loading RAG graph..."):
        st.session_state.graph = build_rag_graph()


# ── Sidebar: settings + source docs ─────────────────────────────────────────

with st.sidebar:
    st.title("Move Mind AI")
    st.caption("RAG pipeline powered by LangGraph")
    st.divider()

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.divider()
    st.markdown("**Last retrieved sources:**")
    sources_container = st.container()


# ── Chat history ─────────────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ── Chat input ───────────────────────────────────────────────────────────────

if prompt := st.chat_input("Ask about the AMS Admin Tool..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run the graph with node-level streaming for status updates
    with st.chat_message("assistant"):
        status = st.status("Thinking...", expanded=True)
        answer_placeholder = st.empty()
        graph = st.session_state.graph
        config = {"configurable": {"thread_id": st.session_state.thread_id}}

        documents = []
        answer = ""

        for event in graph.stream({"question": prompt}, config=config):
            # Each event is {node_name: {state_updates}}
            for node_name, output in event.items():
                if node_name in _STATUS_LABELS:
                    status.write(_STATUS_LABELS[node_name])

                if node_name == NODE_RETRIEVE_DOCS:
                    documents = output.get("documents", [])
                    status.write(f"📄 Retrieved **{len(documents)}** chunks")

                elif node_name == NODE_GENERATE_ANSWER:
                    answer = output.get("answer", "")

        status.update(label="Done", state="complete", expanded=False)
        answer_placeholder.markdown(answer)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Show sources in sidebar
    with sources_container:
        if documents:
            for i, doc in enumerate(documents):
                m = doc.metadata
                with st.expander(
                    f"[{i+1}] {m.get('section', 'Untitled')} — {m.get('doc_type', '?')}",
                    expanded=False,
                ):
                    st.caption(f"📄 {m.get('source', '?')}")
                    st.caption(f"📂 {m.get('doc_title', '?')}")
                    st.markdown(doc.page_content[:500])
        else:
            st.info("No sources yet. Ask a question!")
