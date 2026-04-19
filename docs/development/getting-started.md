# Getting Started

Goal: from a fresh clone to a working local dev loop in under 30 minutes.

## 1. Prerequisites

Install once, reuse forever.

| Tool       | Version      | Install                                                       |
| ---------- | ------------ | ------------------------------------------------------------- |
| Git        | any recent   | system package manager                                         |
| Node       | **22.x LTS** | `nvm install 22 && nvm use 22` (repo pins via `.nvmrc`)        |
| pnpm       | **9.12+**    | `corepack enable && corepack prepare pnpm@9.12.0 --activate`   |
| Python     | **3.13**     | `uv python install 3.13` (see next row for uv)                 |
| uv         | **0.4+**     | `curl -LsSf https://astral.sh/uv/install.sh \| sh`              |
| Docker     | any recent   | Docker Desktop or OrbStack                                     |
| gitleaks   | optional     | `brew install gitleaks` — pre-commit skips if missing          |

### Why these tools

- **pnpm** (not npm/yarn): fast, strict, content-addressable; our lockfile is `pnpm-lock.yaml`.
- **uv** (not pip/poetry): fast, lockfile-first; resolves and installs in one command.
- **corepack**: ships with Node, pins the pnpm version so everyone uses the same.

## 2. Clone and configure git identity

```bash
git clone <repo-url>
cd move-mind-ai
```

### Git identity

This repo uses a **repo-local git identity** so commits never leak your corporate identity. Configure it once per clone:

```bash
git config user.name  "<your personal name>"
git config user.email "<your personal email>"
# Do NOT use --global here.
```

Verify:

```bash
git config user.email   # should print your personal email
```

If the output is your corporate email, you have not scoped it locally — re-run with `user.email` and *no* `--global`.

## 3. Install dependencies

### Backend

```bash
cd backend
uv sync                          # installs prod + dev deps into .venv
cd ..
```

### Frontend

```bash
cd frontend
pnpm install                     # also sets git hooksPath via the `prepare` script
cd ..
```

After `pnpm install`, verify hooks are wired:

```bash
git config core.hooksPath
# expected: .husky
```

If empty, run `pnpm --prefix frontend run prepare` from repo root.

## 4. Configure environment

Copy the example env and fill in real values:

```bash
cp .env.example backend/.env      # if you have access to keys
```

At minimum you need: `OPENAI_API_KEY`, `PINECONE_API_KEY`, and the LangSmith project variables if you want tracing. Without keys, non-integration tests still run; only live requests fail.

## 5. First run

### Backend (FastAPI)

```bash
cd backend
uv run uvicorn app.api.app:app --reload --port 8000
```

Smoke check: `curl http://localhost:8000/health` → `{"status":"ok"}`.

### Frontend (rsbuild dev server)

```bash
cd frontend
pnpm dev                          # http://localhost:3000
```

The app proxies `/api` and `/health` to the backend (see `frontend/rsbuild.config.ts`). If the backend is running you should see the health chip turn green.

### Both together (Docker)

```bash
docker compose up                 # backend 8000 + frontend 3000
```

## 6. Verify your toolchain is healthy

Run this once before your first commit. Everything should pass.

```bash
# From frontend/
pnpm typecheck
pnpm lint
pnpm format:check
pnpm test:coverage
pnpm build
```

```bash
# From backend/
uv run pytest -m "not integration"
```

If any of these fail on a clean clone, that is a repo bug — open an issue.

## 7. Make your first commit

Create a branch that follows convention:

```bash
git checkout -b feat/my-first-change
```

Make a small edit, stage it, and commit:

```bash
git add <file>
git commit -m "docs(dev): note that I read the onboarding"
```

What happens automatically:

- **pre-commit**: `lint-staged` runs ESLint + Prettier on staged frontend files; gitleaks scans for secrets (if installed).
- **commit-msg**: commitlint rejects the commit if the message does not follow conventional-commits.
- **pre-push**: rejects the push if the branch name does not match `<type>/<kebab>`.

If a hook fails, fix the issue and re-commit — do **not** use `--no-verify`.

## 8. Next steps

- Read [`workflow.md`](workflow.md) for the PR flow.
- Read [`code-style.md`](code-style.md) for conventions.
- If you are touching `frontend/src/`, open [`../../agents/frontend/README.md`](../../agents/frontend/README.md) and follow the routing table.
