# Contributing to Move Mind AI

Welcome. This file is the front door for anyone — human or agent — writing code in this repo.

## What is this project?

Move Mind AI is a **generic, multi-tenant AI log-debugging SaaS**. CMS3 is the first onboarded tenant (reference implementation), not the product. The authoritative product vision lives in [`docs/sow.md`](docs/sow.md). Read it before proposing non-trivial changes.

## Where to start

New here? Read these in order:

1. [`docs/development/getting-started.md`](docs/development/getting-started.md) — prerequisites, setup, first run.
2. [`docs/development/repo-structure.md`](docs/development/README.md#repo-structure) *(in the dev README)* — what lives where.
3. [`docs/development/workflow.md`](docs/development/workflow.md) — branches, commits, PRs, CI gates.
4. [`docs/development/code-style.md`](docs/development/code-style.md) — conventions and rulebook routing.
5. [`docs/development/troubleshooting.md`](docs/development/troubleshooting.md) — known snags.

For deep project/tooling context (commands, architecture, audit posture), see [`CLAUDE.md`](CLAUDE.md). It is the source of truth for how the repo is organized and which guardrails apply.

## The non-negotiables

Before you open a PR, you must be aligned with:

- **Audit-readiness posture.** This repo is built to pass third-party audit from day one. See [`SECURITY.md`](SECURITY.md) and [`docs/audit/controls-matrix.md`](docs/audit/controls-matrix.md).
- **No AI attribution.** Commits and PRs appear under the author's personal identity only. No `Co-Authored-By: Claude`, no "Generated with Claude Code" footer.
- **Personal git identity.** This repo uses a repo-local git identity. Before your first commit, set `user.name` and `user.email` locally (`git config user.email ...`, no `--global`). See [`docs/development/getting-started.md`](docs/development/getting-started.md#git-identity).
- **Conventional commits + branch naming.** Enforced by husky locally and CI on PR. Branch: `<type>/<kebab-description>` (types: `feat|fix|chore|docs|refactor|test|perf|ci|build|revert|style`). Commit: `<type>(<scope>): <subject>`.
- **Agent rulebooks are binding.** If you are touching `frontend/src/`, open [`agents/frontend/README.md`](agents/frontend/README.md) first and follow the routing table to the relevant rulebook(s).

## Reporting security issues

Do **not** open a public issue. Email `souravmajumdar.developer@gmail.com` with `[SECURITY]` in the subject. Full policy: [`SECURITY.md`](SECURITY.md).

## Questions

Open a GitHub issue with the `question` label, or reach out to the maintainer directly.
