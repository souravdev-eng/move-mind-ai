# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Product framing (read this first)

MoveMind AI is a **generic, multi-tenant AI log-debugging SaaS**, not a CMS3 tool. CMS3 is the first/reference project onboarded — it is the tenant, not the product. The authoritative product vision, target architecture, and phased delivery plan live in `docs/sow.md` (v1.1); read it before making non-trivial changes.

- **v1 (current code in this repo)** is hand-tuned for CMS3 as the reference implementation. Several layers contain CMS3-specific hardcoding (fields, prompts, namespace, state). This is acknowledged, intentional, and enumerated in SOW §2 and §4.
- **v2 (target)** replaces CMS3 coupling with a descriptor-driven generic agent per SOW §5 and Phase 1+. The direction is: agent logic stays constant; per-project knowledge lives in a user-confirmed YAML descriptor.

**Implication for edits:** prefer changes that generalize cleanly. When touching CMS3-specific code, think about how it would be expressed as descriptor-driven logic in v2, and avoid adding *new* CMS3 hardcoding unless explicitly scoped to v1 stabilization.

## Repo layout

Monorepo with two deployables wired together by `docker-compose.yml`:

- `backend/` — Python 3.13 FastAPI + LangGraph RAG service. Dependency-managed with `uv` (`pyproject.toml`, `uv.lock`). All source lives under `backend/app/`; CLIs live in `backend/scripts/`.
- `frontend/` — React 19 + MUI + rsbuild SPA (early scaffold). Package manager is `pnpm`. Talks to the backend via `RSBUILD_APP_API_URL`.
- `agents/` — repo-scoped agent rulebooks (currently `agents/frontend/*.md` covering architecture, state, streaming, styling, testing, typescript, ui_ux, observability, etc.). Consult the relevant file before making frontend changes.
- `docs/sow.md` — product statement of work (the source of truth for product direction). Per-feature teaching docs live in `backend/docs/features/`; sprint/tracking docs in `backend/docs/tracking/`.

The repo was restructured into `backend/` + `frontend/` recently — older `app/` paths in the root `README.md` are out of date. Trust `backend/` layout.

## Common commands

All backend commands assume `cd backend`.

```bash
# Setup
uv sync                                            # install deps (including dev)

# Run (choose one)
uv run uvicorn app.api.app:app --reload --port 8000
uv run streamlit run app/ui/streamlit_app.py      # legacy UI; being replaced by frontend/
bash scripts/run_all.sh                           # FastAPI + Streamlit together
python main.py                                    # CLI entry point

# Ingestion (populate Pinecone from processed chunks)
uv run python scripts/ingest.py
uv run python scripts/upload_dataset.py           # push golden dataset to LangSmith

# Tests
uv run pytest                                     # full suite
uv run pytest -m "not integration"                # skip live-API integration tests
uv run pytest tests/test_rag.py::test_name        # single test

# Eval pipeline (Ragas + custom metrics + optional LangSmith experiment)
bash scripts/run_eval.sh                          # run + diff vs baseline
bash scripts/run_eval.sh --update-baseline        # accept current as new baseline
bash scripts/run_eval.sh --skip-langsmith         # local-only
bash scripts/check_regression.sh                  # regression gate (exit non-zero on drop)
uv run python -m app.eval.cli --output data/eval/latest_results.json
uv run python -m app.eval.diff --current ... --baseline ...
```

Frontend (from `frontend/`):

```bash
pnpm install
pnpm dev                  # rsbuild dev server on :3000
pnpm build
pnpm test                 # vitest run
pnpm lint
pnpm format:check
```

Full-stack via Docker: `docker compose up` (backend 8000, frontend 3000; backend env from `backend/.env`).

## Architecture

### Backend: LangGraph log-debugging agent (v1 — CMS3 reference implementation)

The product is generic; the v1 implementation is CMS3-tuned. Single compiled graph in `app/graphs/agent.py`, built from typed state (`app/graphs/state.py`) and node functions in `app/graphs/nodes/`. Wiring:

```
classify_question ──► (retrieve | rewrite)
rewrite_question  ──► resolve_context
                       │
resolve_context   ──► retrieve_docs ──► rerank_docs ──► generate_answer ──► classify_issue ──► END
```

Key facts when editing the graph:

- State transitions must go through `GraphState` fields — nodes return partial dict updates, never mutate.
- Node names are centralized in `app/graphs/constants.py`. Use the constants, not string literals.
- The graph is compiled with `MemorySaver()` for thread-scoped conversation memory. `graph.png` is auto-regenerated on compile — do not hand-edit.
- `classify_question` routes between a direct-retrieval path and a query-rewrite path; `classify_issue` is a post-answer labeler (not a router).

### Chains vs graphs

`app/chains/` holds stateless prompt→LLM→parser pipelines (`answer_chain`, `classify_chain`, `query_rewrite_chain`, `reranker_chain`). They are invoked from nodes; do not add control flow inside a chain. Anything with branching/loops belongs in `app/graphs/`.

### RAG layer

`app/rag/` is split by stage:

- `preprocessing.py` + `chunks_loader.py` — produce `data/processed/cms3_log_chunks.json` from raw CMS3 logs.
- `ingestion.py` + `pinecone_store.py` — embed and upsert to Pinecone (namespace `cms3-logs`). FAISS code exists historically but Pinecone is the production store.
- `retrieval.py` + `retriever_registry.py` — registry-keyed retrievers so the graph can pick between e.g. summary vs event retrievers (`RETRIEVER_SUMMARY_K`, `RETRIEVER_EVENT_K`).
- Reranking uses FlashRank (`FLASHRANK_MODEL_NAME`) after retrieval; top-N controlled by `RERANK_TOP_N`.

### Config

`app/config.py` loads a single `Settings` object via `pydantic-settings`. Never call `os.getenv` directly in app code. Model tiers are named by capability, not vendor: `OPENAI_FAST`, `OPENAI_SMART`, `OPENAI_THINKING` — pick the tier appropriate to the node (classifiers use FAST, generation uses SMART).

### Observability & eval

- `app/obs/tracing.py` + `app/obs/pricing.py` — LangSmith tracing and per-call cost/latency tracking. Tracing is gated on `LANGCHAIN_TRACING_V2`; the project name routes by environment (`LANGCHAIN_PROJECT_DEV` / `_EVAL` / `_PROD`, falling back to `LANGCHAIN_PROJECT`). When adding a node that calls an LLM, inherit the traced runnable context — don't bypass with raw client calls.
- `app/eval/` — offline eval lives here. `runner.py` executes the graph across the golden dataset; `metrics.py` computes Ragas + custom metrics; `diff.py` compares current vs `data/eval/baseline_results.json` and is the regression gate; `langsmith_evaluators.py` is used by `scripts/run_langsmith_eval.py` for online experiments. Baselines are committed — update them with `--update-baseline` only when a change is intentional.

### API

`app/api/app.py` is the FastAPI factory. Routes live in `app/api/routes/` (thin: parse → call graph/chain → return). Add new routes as new files and register in `app.py`. Business logic never lives in a route.

### Frontend

React 19 + MUI v6 + rsbuild + TypeScript, tested with Vitest + Testing Library. Current state under `frontend/src/` is an early scaffold (`App.tsx`, `theme.ts`, `index.tsx`) — the backend is still served primarily by the legacy Streamlit UI (`backend/app/ui/streamlit_app.py`), which this frontend is replacing.

Before making frontend changes, read the relevant rulebook in `agents/frontend/` — these files are the project's conventions for architecture, state management, streaming (SSE from `/api/v1/chat`), styling, testing, TypeScript, UI/UX, observability, and component patterns. Treat them as binding, not advisory.

Backend URL comes from `RSBUILD_APP_API_URL` (rsbuild convention — env vars must be prefixed `RSBUILD_` to be exposed to client code).

## Conventions

- Imports from backend code are always absolute: `from app.x.y import z` (enabled by `cd backend` being the runtime root).
- Tests mirror `app/` layout under `backend/tests/`. Integration tests require live API keys and are marked `@pytest.mark.integration` — skip them with `-m "not integration"` when iterating without secrets.
- Docs under `backend/docs/features/` follow a pedagogical teaching style (pain → mental model → trade-offs → FAQ); `backend/docs/tracking/` holds sprint state. Update tracking docs when finishing work items there.
- `.env` lives at `backend/.env` (see `.env.example` at repo root for the full variable set, including Pinecone, LangSmith per-env projects, and retrieval knobs).
