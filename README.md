# Move Mind AI

GenAI application powered by **LangChain**, **LangGraph**, and **RAG**.

## Project Structure

```
move-mind-ai/
├── app/                        # Main application package
│   ├── __init__.py
│   ├── config.py               # Central settings (loaded from .env)
│   ├── chains/                 # LangChain chains (prompt → LLM → parser)
│   │   ├── __init__.py
│   │   └── base.py
│   ├── graphs/                 # LangGraph agent graphs (stateful workflows)
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── rag/                    # RAG pipeline
│   │   ├── __init__.py
│   │   ├── ingestion.py        # Load → split → embed → persist
│   │   ├── retriever.py        # Retriever factory
│   │   └── chain.py            # Retrieve → prompt → generate
│   ├── prompts/                # Prompt templates
│   │   ├── __init__.py
│   │   └── templates.py
│   ├── api/                    # REST API (FastAPI)
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI app factory
│   │   ├── dependencies.py     # Shared deps (auth, rate-limit, etc.)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py       # GET /health
│   │       └── chat.py         # POST /api/v1/chat
│   ├── tools/                  # Custom tools for agents
│   │   ├── __init__.py
│   │   └── search.py
│   ├── models/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── utils/                  # Shared helpers
│       ├── __init__.py
│       └── helpers.py
├── data/
│   ├── raw/                    # Source documents for ingestion
│   ├── processed/              # Intermediate artifacts
│   └── vectorstore/            # Persisted FAISS index
├── notebooks/                  # Jupyter notebooks for experimentation
├── scripts/
│   └── ingest.py               # CLI ingestion script
├── tests/
│   ├── test_chains.py
│   ├── test_graphs.py
│   └── test_rag.py
├── .env.example                # Environment variable template
├── .gitignore
├── pyproject.toml
├── main.py                     # CLI entry point
└── README.md
```

## Architecture & Thought Process

This section explains **why** the project is organized this way. Use it as a reference whenever you're unsure where something belongs.

### Why everything lives inside `app/`

All application code sits under a single `app/` Python package. This gives us:

- **Clean imports** — `from app.rag.chain import build_rag_chain` reads like plain English.
- **Isolation from project root** — Config files (`pyproject.toml`, `.env`), scripts, tests, and data stay at the root without mixing with source code.
- **Easy packaging** — If you ever need to publish or containerize the app, `app/` is the only directory you ship.

### Folder-by-folder breakdown

#### `app/config.py` — Single source of truth for settings

Every AI project juggles API keys, model names, chunk sizes, and feature flags. Instead of scattering `os.getenv()` calls everywhere, **one `Settings` class** loads everything from `.env` and exposes typed attributes. Any file can simply do `from app.config import settings`.

> **Rule of thumb:** If a value might change between environments (dev / staging / prod), it belongs in `config.py`.

#### `app/chains/` — Stateless LangChain pipelines

A "chain" is a straight-line pipeline: **prompt → LLM → output parser**. No loops, no branching, no memory.

- Put simple Q&A chains, summarization chains, or classification chains here.
- Each file defines one or more chain-builder functions (e.g., `build_simple_chain()`).

> **When to use chains vs graphs:** If there's no decision-making or looping, it's a chain. If the LLM needs to decide "should I call a tool or respond?" — that's a graph.

#### `app/graphs/` — Stateful LangGraph agent workflows

LangGraph lets you build **multi-step, branching, looping** agent workflows as a state machine. Each graph has:

- **State** — a `TypedDict` describing what data flows through the graph.
- **Nodes** — functions that transform the state (call an LLM, run a tool, etc.).
- **Edges** — connections between nodes, including conditional routing.

Use this folder when you need an agent that can reason over multiple turns, call tools, or follow a complex decision tree.

#### `app/rag/` — The RAG pipeline (ingestion → retrieval → generation)

RAG is split into three clear stages, each in its own file:

| File | Stage | What it does |
| --- | --- | --- |
| `ingestion.py` | **Ingest** | Load documents → split into chunks → embed → save to vector store |
| `retriever.py` | **Retrieve** | Load the persisted vector store and return a LangChain retriever |
| `chain.py` | **Generate** | Combine the retriever + prompt + LLM into a runnable RAG chain |

This separation means you can re-run ingestion independently (e.g., when new docs arrive) without touching the retrieval or generation logic.

#### `app/prompts/` — Centralized prompt management

All prompt templates live here, not scattered inside chain/graph files. Benefits:

- **Easy to review** — Product / domain experts can audit prompts in one place.
- **Reusable** — Multiple chains or graphs can share the same prompt.
- **Version-friendly** — Prompt changes show up as clean git diffs.

#### `app/api/` — REST API layer (FastAPI)

This is the **HTTP interface** to your AI pipelines. The structure follows FastAPI best practices:

- `app.py` — The app factory. Creates the FastAPI instance and registers routers.
- `routes/` — One file per resource or domain (`chat.py`, `health.py`). Add more as you grow (e.g., `ingest.py`, `agents.py`).
- `dependencies.py` — Shared `Depends()` logic like API key validation, rate limiting, or DB session management.

> **Key idea:** Routes are thin. They validate the request, call a chain/graph/RAG pipeline from another module, and return the result. Business logic never lives in a route file.

#### `app/tools/` — Custom tools for agents

LangGraph agents use "tools" to interact with the outside world (search the web, query a database, call an API). Each tool is a Python function decorated with `@tool`.

- One file per tool or per tool category (e.g., `search.py`, `database.py`, `calculator.py`).
- Tools are imported and bound to the agent in `app/graphs/`.

#### `app/models/` — Pydantic schemas

Request/response shapes for the API, structured output schemas for LLMs, and any shared data models. Keeping these separate from routes and chains avoids circular imports and makes validation reusable.

#### `app/utils/` — Shared helpers

Small, generic utilities (logging setup, text cleaning, token counting) that don't belong to any specific module. If a helper is only used by one module, keep it in that module instead.

### Folders outside `app/`

| Folder | Purpose |
| --- | --- |
| `data/raw/` | Drop your source documents here (PDFs, text files, etc.) before ingestion |
| `data/processed/` | Intermediate artifacts (cleaned text, extracted tables, etc.) |
| `data/vectorstore/` | The persisted FAISS (or other) index — **auto-generated, git-ignored** |
| `notebooks/` | Jupyter notebooks for experimentation and prototyping. Not imported by `app/` |
| `scripts/` | Standalone CLI utilities (e.g., `ingest.py`). Thin wrappers that call into `app/` |
| `tests/` | Mirrors `app/` structure. One test file per module |

### How data flows through the project

```
User Request
     │
     ▼
 app/api/routes/     ← HTTP entry point (FastAPI)
     │
     ▼
 app/chains/         ← Simple pipeline?  OR
 app/graphs/         ← Complex agent workflow?
     │
     ├──▶ app/prompts/    (prompt templates)
     ├──▶ app/tools/      (external tool calls)
     ├──▶ app/rag/        (retrieval-augmented generation)
     │       │
     │       ├──▶ retriever.py  → vector store lookup
     │       └──▶ chain.py      → prompt + LLM + retrieved context
     │
     ▼
 app/models/         ← Validate & shape the response
     │
     ▼
 JSON Response
```

### Quick decision guide: "Where do I put this?"

| You want to… | Go to… |
| --- | --- |
| Add a new API endpoint | `app/api/routes/` — create a new file, register in `app.py` |
| Build a simple prompt → LLM pipeline | `app/chains/` |
| Build an agent with tool-calling or loops | `app/graphs/` |
| Add / modify a prompt template | `app/prompts/templates.py` |
| Create a new tool for an agent | `app/tools/` |
| Add a new request/response schema | `app/models/schemas.py` |
| Change an API key or model name | `.env` (runtime) or `app/config.py` (defaults) |
| Add source documents for RAG | `data/raw/` then run `python scripts/ingest.py` |
| Experiment with something new | `notebooks/` |
| Write a test | `tests/` |

## Quick Start

```bash
# 1. Clone & enter the project
cd move-mind-ai

# 2. Create a virtual environment & install dependencies
uv sync                     # or: pip install -e ".[dev]"

# 3. Set up environment variables
cp .env.example .env        # then fill in your API keys

# 4. Run the app
python main.py
```

## Key Modules

| Module          | Purpose                                             |
| --------------- | --------------------------------------------------- |
| `app/api/`      | FastAPI REST endpoints (routes, dependencies)       |
| `app/chains/`   | Composable LangChain chains (prompt → LLM → parser) |
| `app/graphs/`   | LangGraph stateful agent workflows                  |
| `app/rag/`      | Full RAG pipeline: ingestion, retrieval, generation |
| `app/prompts/`  | Centralized prompt template management              |
| `app/tools/`    | Custom tools callable by LangGraph agents           |
| `app/models/`   | Pydantic request/response schemas                   |
| `app/config.py` | Single source of truth for all settings             |

## Ingestion

Place source documents in `data/raw/`, then run:

```bash
python scripts/ingest.py
```

## Running the API Server

```bash
uvicorn app.api.app:app --reload --port 8000
```

Endpoints:

- `GET  /health` – health check
- `POST /api/v1/chat` – send a message, get an AI response

## Testing

```bash
pytest tests/
```

---

## Notebook Learning Path

The `notebooks/` directory is a structured, hands-on curriculum for building production-grade RAG systems. Each notebook is self-contained and runnable — use them as reference when building the actual `app/` code.

> **Kernel:** Always select the `.venv (Python 3.13.5)` kernel before running.

| # | Notebook | What You Learn | Key Concepts |
| --- | --- | --- | --- |
| 1 | `1-data-preprocessing.ipynb` | Parse raw markdown docs into enriched chunks | Heading-aware splitting, `MarkdownHeaderTextSplitter` + `RecursiveCharacterTextSplitter`, metadata enrichment (doc_type, audience, section hierarchy) |
| 2 | `2-ingestion.ipynb` | Embed chunks and build a vector index | OpenAI `text-embedding-3-small` (1536 dims), FAISS index, persist/load from disk, validation queries |
| 3 | `3-retrieval.ipynb` | Compare retrieval strategies | Baseline similarity search, metadata filtering, multi-query retriever (LLM generates query variants), relevance scores, out-of-domain detection |
| 4 | `4-langgraph-rag.ipynb` | Build a LangGraph RAG flow | `route_query → retrieve_docs → generate_answer`, LLM-based router, retriever registry (extensible to multiple knowledge bases) |
| 5 | `5-evaluation.ipynb` | Measure RAG quality objectively | Golden eval dataset, LLM-as-judge (faithfulness, answer relevance, context relevance), Ragas framework, retrieval hit rate, saved results for comparison |
| 6 | `6-memory.ipynb` | Multi-turn conversations | Question condensation (rewrite follow-ups), `MemorySaver` checkpointer, thread-based isolation, chat history in prompts |
| 7 | `7-reranking.ipynb` | Improve precision after retrieval | Over-retrieve (k=15) → LLM rerank → keep top-5, bi-encoder vs cross-encoder tradeoff, rerank node in LangGraph |
| 8 | `8-hybrid-search.ipynb` | Combine keyword + semantic search | BM25 retriever, Reciprocal Rank Fusion (RRF), ensemble weights, when BM25 beats vector search |
| 9 | `9-adaptive-rag.ipynb` | Self-correcting RAG with quality gates | Document grading, hallucination detection, usefulness check, query rewriting, conditional edges, retry budget |

### Recommended Run Order

```
1-data-preprocessing  →  2-ingestion  →  3-retrieval  →  4-langgraph-rag
                                                              ↓
                         5-evaluation  ←  run after any pipeline change
                                                              ↓
                      6-memory  →  7-reranking  →  8-hybrid-search  →  9-adaptive-rag
```

### From Notebooks to App

Each notebook teaches a pattern you can pull into `app/`:

| Notebook | Maps to                | What to extract                                  |
| -------- | ---------------------- | ------------------------------------------------ |
| 1–2      | `app/rag/ingestion.py` | Chunking strategy, embedding config              |
| 3        | `app/rag/retriever.py` | Retriever factory with configurable strategy     |
| 4        | `app/graphs/agent.py`  | Graph structure, router node, retriever registry |
| 5        | `tests/test_rag.py`    | Eval harness as CI/CD quality gate               |
| 6        | `app/graphs/agent.py`  | Add checkpointer + condense node                 |
| 7        | `app/rag/retriever.py` | Add rerank step after retrieval                  |
| 8        | `app/rag/retriever.py` | Hybrid BM25+vector retriever                     |
| 9        | `app/graphs/agent.py`  | Full adaptive graph with conditional edges       |

---

## RAG Concepts Reference

Quick reference for the core concepts used across this project.

### Chunking

- **Strategy:** Heading-aware splitting → `MarkdownHeaderTextSplitter` preserves document structure, then `RecursiveCharacterTextSplitter` enforces size limits
- **Config:** 1000 chars per chunk, 200 char overlap
- **Metadata:** Each chunk carries `source`, `doc_type`, `section`, `heading_hierarchy`, `chunk_index`

### Embeddings

- **Model:** OpenAI `text-embedding-3-small` (1536 dimensions)
- **Why:** Good balance of quality, speed, and cost for technical docs

### Vector Store

- **Engine:** FAISS (CPU) — fast, local, no infrastructure needed
- **Persistence:** Saved to `data/vectorstore/` (index.faiss + index.pkl)

### Retrieval Strategies

| Strategy             | Recall   | Precision | Latency | Best For                |
| -------------------- | -------- | --------- | ------- | ----------------------- |
| Baseline (k=5)       | Moderate | Good      | Fast    | Simple queries          |
| Metadata filter      | Targeted | High      | Fast    | Scoped questions        |
| Multi-query          | High     | Moderate  | Slower  | Ambiguous questions     |
| Reranking            | High     | High      | Slower  | When precision matters  |
| Hybrid (BM25+vector) | Highest  | Good      | Medium  | Exact terms + semantics |
| Adaptive             | High     | Highest   | Slowest | Production reliability  |

### Evaluation Metrics

| Metric             | What It Measures                                 |
| ------------------ | ------------------------------------------------ |
| Faithfulness       | Is the answer grounded in the retrieved context? |
| Answer Relevance   | Does the answer address the question?            |
| Context Relevance  | Are the retrieved chunks relevant?               |
| Context Precision  | Are relevant chunks ranked higher?               |
| Context Recall     | Did we retrieve everything needed?               |
| Retrieval Hit Rate | Did the expected source appear in top-k?         |

---

## Future Roadmap

### Level 1 — Production App

- [ ] FastAPI serving with streaming SSE (`astream_events`)
- [ ] WebSocket chat UI (React/Next.js)
- [ ] LangSmith tracing (config already in `.env.example`)
- [ ] Persistent memory (`PostgresSaver` / `SqliteSaver`)

### Level 2 — Robustness & Scale

- [ ] Incremental ingestion (re-embed only changed docs)
- [ ] Document CRUD API (add/update/delete from vectorstore)
- [ ] Semantic caching (Redis or LangChain cache)
- [ ] Guardrails (PII detection, prompt injection defense)
- [ ] Rate limiting & authentication

### Level 3 — Advanced RAG

- [ ] Agentic RAG with tool calling (LLM decides when to retrieve)
- [ ] Multi-index routing (5+ specialized knowledge bases)
- [ ] Parent-child retrieval (small chunks for search, large chunks for context)
- [ ] Semantic chunking (split by meaning, not character count)
- [ ] Knowledge graph RAG (Neo4j for relational reasoning)

### Level 4 — Intelligence & Optimization

- [ ] Fine-tuned embeddings on domain-specific data
- [ ] Prompt optimization (DSPy / auto-tuning with eval dataset)
- [ ] A/B testing (serve two graph variants, compare scores)
- [ ] User feedback loop (thumbs up/down → improve retrieval)
- [ ] Multi-modal RAG (embed architecture diagrams + screenshots)

### Level 5 — Platform

- [ ] Multi-tenant (per-team indexes and permissions)
- [ ] CI/CD eval gate (block deploys if scores drop)
- [ ] Cost monitoring (tokens per query, embedding costs)
- [ ] Observability dashboard (latency, hit rate, hallucination rate)
