# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Setup:**
```bash
uv sync                        # Install all dependencies (uses UV, not pip)
cp .env.example .env           # Fill in OpenAI + Pinecone keys
```

**Run servers:**
```bash
uvicorn app.api.app:app --reload --port 8000   # FastAPI backend
streamlit run app/ui/streamlit_app.py --server.port 8501  # Streamlit UI
bash scripts/run_all.sh        # Start both simultaneously
```

**Ingest data:**
```bash
python scripts/ingest.py                       # Ingest from data/raw/
python scripts/ingest.py --source data/raw
```

**Lint & format:**
```bash
ruff check app/
black app/
isort app/
```

**Tests:**
```bash
pytest tests/
pytest tests/test_chains.py    # Run a single test file
```

## Architecture

This is a RAG (Retrieval-Augmented Generation) system for debugging CMS3 execution logs. Users ask natural-language questions; the system retrieves relevant log chunks from Pinecone and generates grounded answers.

### Request Flow

```
POST /api/v1/chat
  → LangGraph RAG Graph (stateful, thread-per-session)
      → classify_question  (fast LLM: gpt-4o-mini)
      → rewrite_question   (if follow-up, condense with history)
      → resolve_context    (regex-extract CID, execution_id, page_path)
      → retrieve_docs      (Pinecone: 2 summaries + 8 events, metadata-scoped)
      → rerank_docs        (FlashRank top-5; skipped for API timeline queries)
      → generate_answer    (smart LLM: gpt-4o or o3)
  → ChatResponse (sync) or SSE token stream
```

### Key Layers

- **`app/config.py`** — All settings via Pydantic `BaseSettings`. Multi-model LLM presets: `OPENAI_FAST` (gpt-4o-mini), `OPENAI_SMART` (gpt-4o), `OPENAI_THINKING` (o3).
- **`app/graphs/`** — LangGraph stateful workflow. `agent.py` builds the graph; `state.py` defines `GraphState` (TypedDict). `MemorySaver` provides per-thread chat history.
- **`app/chains/`** — Thin LangChain pipelines (prompt → LLM → output parser) used by graph nodes.
- **`app/rag/retrieval.py`** — Core retrieval logic. Detects "API timeline" queries (keywords: apis, graphql, request, endpoint) and builds structured markdown output instead of running similarity search. Regular queries run metadata-filtered Pinecone search.
- **`app/rag/preprocessing.py`** — Normalizes raw CMS3 JSON logs into two chunk types: `execution_summary` (condensed journey overview) and `event` (individual log entry with rich metadata).
- **`app/prompts/templates.py`** — All prompt templates live here. Edit prompts here, not inline in chains/nodes.
- **`app/api/dependencies.py`** — Singleton initialization of the RAG graph. The graph is built once at startup and reused across requests.

### Data & Chunking

Raw logs live in `data/raw/cms3-logs.json`. The ingestion pipeline normalizes them into chunks with metadata fields: `customer_id`, `execution_id`, `step_order`, `action`, `page_path`, `decision_result`. These metadata fields drive Pinecone filter-scoped retrieval.

### LLM Selection

Node-level LLM selection is intentional:
- Classification & rewriting → fast/cheap model
- Answer generation → smart model; switches to `OPENAI_THINKING` for complex analytical questions

### Streaming

`POST /api/v1/chat` with `"stream": true` returns Server-Sent Events. Event types: `session`, `status` (node name), `retrieval`, `rerank`, `token`, `sources`, then `[DONE]`.
