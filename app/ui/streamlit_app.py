"""Streamlit chat UI for the Move Mind AI RAG pipeline.

Run:
    streamlit run app/ui/streamlit_app.py

This is a temporary frontend. Delete app/ui/ when migrating to React.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so `app.*` imports work
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from app.graphs.agent import build_rag_graph
from app.utils.helpers import get_logger

logger = get_logger(__name__)


# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Move Mind AI",
    page_icon="🧠",
    layout="wide",
)


# ── Session state init ───────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

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

    # Run the graph
    with st.chat_message("assistant"):
        status = st.status("Thinking...", expanded=True)
        graph = st.session_state.graph

        # Step 1: Route
        status.write("🔀 Routing query...")
        result = graph.invoke({"question": prompt})

        retriever_name = result.get("retriever_name", "?")
        status.write(f"📚 Retriever: **{retriever_name}**")

        # Step 2: Retrieved docs count
        documents = result.get("documents", [])
        status.write(f"🔍 Retrieved **{len(documents)}** chunks")

        # Step 3: Answer
        answer = result.get("answer", "")
        status.update(label="Done", state="complete", expanded=False)

        st.markdown(answer)

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
