# Workflow: branches, commits, PRs, CI

## Mental model

Work flows through four checkpoints, each owned by a different mechanism:

1. **Your branch name** — checked by husky `pre-push` and CI `security-ci/branch-name`.
2. **Your commit messages** — checked by husky `commit-msg` and CI `security-ci/commits`.
3. **Your diff** — checked by husky `pre-commit` (lint-staged) and CI `frontend-ci` / `backend-ci`.
4. **Your PR** — checked by CODEOWNERS review + all CI workflows green.

If any checkpoint fails, fix the root cause. Do **not** use `--no-verify` or push-force past CI.

## Branching

### Naming

Pattern: `<type>/<kebab-description>`

| Type       | When to use                                           |
| ---------- | ----------------------------------------------------- |
| `feat`     | A user-facing feature                                 |
| `fix`      | A user-facing bug fix                                 |
| `chore`    | Non-functional repo work (dep bumps, tooling)         |
| `docs`     | Documentation only                                    |
| `refactor` | Internal rework, no behavior change                   |
| `test`     | Adding or fixing tests only                           |
| `perf`     | Performance improvement with measurable impact        |
| `ci`       | CI/CD workflow changes                                |
| `build`    | Build system, bundler, or dep-graph changes           |
| `revert`   | Reverting a prior commit/PR                           |
| `style`    | Formatting / cosmetic (rare — prettier normally)      |

Exempt patterns: `main`, `master`, `develop`, `release/<name>`, `hotfix/<name>`.

**Good:** `feat/chat-sse-stream`, `fix/theme-flicker-on-mount`, `refactor/rag-retriever-registry`
**Bad:** `saurav/stuff`, `test`, `FEAT_auth`, `my-branch`

### Starting work

```bash
git checkout main
git pull
git checkout -b feat/my-work
```

## Commit messages

### Format

```
<type>(<scope>): <subject>

<body — optional, explain why if non-obvious>

<footer — optional, e.g. BREAKING CHANGE or issue refs>
```

Rules (enforced by `commitlint`):

- **Type** must be one of the branch types above.
- **Scope** is optional but recommended — e.g. `feat(chat): add streaming token buffer`.
- **Subject** is lowercase, imperative ("add", not "adds" or "added"), no trailing period, ≤ 100 chars total header length.
- **Body** starts after a blank line. Use it to explain *why*, not *what* (the diff shows what).

### Why conventional commits

- Machine-readable — we can auto-generate changelogs, infer semver bumps, and filter history.
- Audit-readable — reviewers see intent at a glance.
- Less bikeshedding — the shape is decided, you just fill it in.

### Examples

```
feat(theme): add persistent light/dark color mode

Stores user selection in localStorage and falls back to prefers-color-scheme.
Accessible toggle lives in the app header.
```

```
fix(api): handle Pinecone timeout in retrieve_docs node

LangGraph node now catches PineconeTimeoutError and surfaces a user-visible
error via the `status` event channel instead of crashing the thread.
```

```
chore(deps): bump @mui/material from 6.4.0 to 6.4.3
```

## Pull requests

### Before you open

- Rebase onto `main`. We prefer a linear history — avoid merge commits into your feature branch.
- Run all local gates (`pnpm typecheck`, `pnpm lint`, `pnpm format:check`, `pnpm test:coverage`, `pnpm build` for frontend; `uv run pytest -m "not integration"` for backend).
- Self-review the diff. Look for: accidental `console.log`, `.only` in tests, temporary env var values, unused imports.

### PR title and description

- **Title:** conventional-commit format (same rules as commit messages). CI validates it.
- **Description:**
  - **What:** one-paragraph summary of the change.
  - **Why:** motivation and context. Link to SOW/issue if relevant.
  - **How:** high-level approach or notable trade-offs.
  - **Test plan:** bulleted checklist of how you verified the change.
  - **Screenshots/GIFs:** required for UI changes.

Keep PRs **small and focused**. If a PR is growing past ~400 changed lines (excluding generated files), split it.

### CI gates (must all pass)

| Workflow           | Jobs                                                               |
| ------------------ | ------------------------------------------------------------------ |
| `frontend-ci.yml`  | typecheck, lint, format:check, test+coverage (≥ 80%), build, audit |
| `backend-ci.yml`   | ruff lint, ruff format:check, pytest (non-integration)             |
| `security-ci.yml`  | gitleaks, commitlint on PR commits, branch-name check              |

### Review and merge

- PRs require at least one CODEOWNER approval.
- Prefer **squash-merge** — the PR title becomes the single merge commit message, so it must be a clean conventional-commit.
- Do not merge your own PR unless the maintainer has explicitly approved.

## What about `--no-verify`?

Never. If a hook is wrong, fix the hook. If a rule is wrong, change the rule (with an accompanying PR explaining why). Bypassing is an audit finding.

## Versioning and releases

Not yet wired — the project is pre-1.0 on the `main` branch. Versioning policy will land when we start cutting tagged releases (tracked in `docs/sow.md` Phase 4+).
