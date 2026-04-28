# Development Documentation

This folder is for **developers working on Move Mind AI**. If you are a first-time contributor, start with [`getting-started.md`](getting-started.md).

## Contents

| File                                                | When to read                                                        |
| --------------------------------------------------- | ------------------------------------------------------------------- |
| [`getting-started.md`](getting-started.md)          | Your first hour. Prereqs, install, run locally, make a first commit.|
| [`workflow.md`](workflow.md)                        | Daily work. Branching, commit convention, PR flow, CI gates.        |
| [`code-style.md`](code-style.md)                    | When you are writing code. Conventions, rulebook routing.           |
| [`troubleshooting.md`](troubleshooting.md)          | When something is broken.                                           |

For product direction and architecture, see [`../sow.md`](../sow.md) and [`../../CLAUDE.md`](../../CLAUDE.md).

## Repo structure

```
move-mind-ai/
├── backend/                    # Python 3.13 — FastAPI + LangGraph RAG service
│   ├── app/                    #   source (absolute imports from `app.*`)
│   │   ├── api/                #   routes + factory
│   │   ├── chains/             #   stateless prompt→LLM→parser pipelines
│   │   ├── graphs/             #   LangGraph state, nodes, agent
│   │   ├── rag/                #   preprocessing, ingestion, retrieval, reranking
│   │   ├── eval/               #   offline Ragas + custom metrics + diff gate
│   │   ├── obs/                #   LangSmith tracing + cost/latency
│   │   └── config.py           #   single Settings object (pydantic-settings)
│   ├── scripts/                #   CLIs: ingest, eval, upload_dataset
│   ├── tests/                  #   pytest (integration marked @pytest.mark.integration)
│   ├── docs/                   #   backend-specific docs (features/, tracking/)
│   └── pyproject.toml          #   uv-managed
├── frontend/                   # React 19 + MUI v6 + rsbuild + TypeScript
│   ├── src/
│   │   ├── atoms/ molecules/ organisms/ pages/   # atomic design
│   │   ├── api/ hooks/ context/ interfaces/      # (see agents/frontend/architecture.md)
│   │   ├── theme/              #   tokens, light/dark themes, ThemeProvider
│   │   ├── test/               #   vitest setup
│   │   ├── App.tsx / index.tsx
│   └── (eslint, prettier, tsconfig, vitest configs)
├── agents/                     # Binding rulebooks for coding agents
│   └── frontend/               #   per-topic rules (architecture, styling, testing, …)
├── docs/
│   ├── sow.md                  #   product statement of work (source of truth)
│   ├── development/            #   you are here
│   └── audit/                  #   audit evidence, controls matrix, dependency policy
├── .github/                    # workflows (frontend-ci, backend-ci, security-ci), CODEOWNERS
├── .husky/                     # git hooks: pre-commit, commit-msg, pre-push
├── CLAUDE.md                   # project instructions (loaded by Claude Code)
├── CONTRIBUTING.md             # onboarding front door
├── SECURITY.md                 # vulnerability disclosure
└── docker-compose.yml          # full-stack dev (backend 8000, frontend 3000)
```

## Naming conventions at a glance

| Thing               | Convention                                                        |
| ------------------- | ----------------------------------------------------------------- |
| Branches            | `<type>/<kebab-description>` (e.g. `feat/theme-toggle`)           |
| Commits             | `<type>(<scope>): <subject>` — conventional-commits               |
| React components    | `PascalCase.tsx`, styles in `PascalCase.style.tsx`                 |
| Hooks               | `useCamelCase.ts` (or `.hook.tsx` for component-owned hooks)      |
| Files (non-comp)    | `kebab-case.ts`                                                   |
| Python modules      | `snake_case.py`                                                   |

See [`code-style.md`](code-style.md) for the full breakdown and [`workflow.md`](workflow.md) for the branch/commit allowlist.
