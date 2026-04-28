---
description: Run pre-commit linting and CI/CD quality gates locally before committing
---

# Pre-commit Checks — Linting & CI/CD

Run the full set of local quality gates that mirror the CI pipelines.
Use this before committing to catch issues early.

---

## 1. Frontend lint-staged (same as Husky pre-commit hook)

Runs ESLint --fix and Prettier on staged `.ts/.tsx` files.

// turbo

```sh
cd frontend && pnpm exec lint-staged
```

## 2. Frontend typecheck

// turbo

```sh
cd frontend && pnpm typecheck
```

## 3. Frontend ESLint (full)

// turbo

```sh
cd frontend && pnpm lint
```

## 4. Frontend format check

// turbo

```sh
cd frontend && pnpm format:check
```

## 5. Frontend tests with coverage (80% threshold)

// turbo

```sh
cd frontend && pnpm test:coverage
```

## 6. Frontend build (catches compile errors)

// turbo

```sh
cd frontend && pnpm build
```

## 7. Frontend dependency audit

// turbo

```sh
cd frontend && pnpm audit --prod --audit-level=high
```

## 8. Backend Ruff lint

// turbo

```sh
cd backend && uv run ruff check .
```

## 9. Backend Ruff format check

// turbo

```sh
cd backend && uv run ruff format --check .
```

## 10. Backend Pytest (non-integration)

```sh
cd backend && OPENAI_API_KEY="dummy-key-for-unit-tests" PINECONE_API_KEY="dummy-key-for-unit-tests" LANGCHAIN_TRACING_V2="false" uv run pytest -m "not integration" --maxfail=1
```

## 11. Gitleaks secret scan on staged files

// turbo

```sh
gitleaks protect --staged --redact --verbose
```

> **Note:** Requires `gitleaks` installed (`brew install gitleaks`). Skipped if not found.

## 12. Commitlint — validate last commit message

// turbo

```sh
cd frontend && pnpm exec commitlint --from HEAD~1 --to HEAD --verbose
```

## 13. Branch name convention check

// turbo

```sh
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo ""); \
if echo "$BRANCH" | grep -Eq '^(main|dev)$'; then echo "✓ Protected branch: $BRANCH"; \
elif echo "$BRANCH" | grep -Eq '^(release|hotfix)/[a-z0-9._-]+$'; then echo "✓ Release/hotfix branch: $BRANCH"; \
elif echo "$BRANCH" | grep -Eq '^(feat|fix|chore|docs|refactor|test|perf|ci|build|revert|style)/[a-z0-9][a-z0-9-]*$'; then echo "✓ Conventional branch: $BRANCH"; \
else echo "✗ Branch '$BRANCH' does not follow convention: <type>/<kebab-description>" && exit 1; fi
```

---

## Quick subsets

- **Frontend only:** Run steps 1–7
- **Backend only:** Run steps 8–10
- **Lint only (no tests):** Run steps 1, 3, 4, 8, 9
- **Security only:** Run steps 11, 12, 13
