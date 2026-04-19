# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Move Mind AI, please **do not open a public issue**. Instead, email the maintainer directly:

- **Contact:** souravmajumdar.developer@gmail.com
- **Subject:** `[SECURITY] <brief description>`

Include the following:

1. A description of the vulnerability and its impact.
2. Steps to reproduce (proof-of-concept if possible).
3. Affected version / commit SHA.
4. Your contact information for follow-up.

You will receive an acknowledgement within **3 business days** and a remediation plan within **10 business days** for confirmed issues.

## Supported Versions

Only the `main` branch receives security fixes during pre-production development. Once a tagged release exists, the current minor version will receive security patches.

## Disclosure Timeline

Coordinated disclosure is the default:

1. Report received and acknowledged (≤ 3 days).
2. Fix developed and tested.
3. Patch released.
4. Public disclosure via GitHub Security Advisory after fix is deployed, or 90 days after report, whichever comes first.

## Scope

In scope:

- The Move Mind AI backend (`backend/`) — FastAPI API, LangGraph agent, RAG pipeline.
- The Move Mind AI frontend (`frontend/`) — React SPA.
- Docker/compose configuration and CI workflows.
- Documentation that could lead to insecure deployment.

Out of scope:

- Vulnerabilities in third-party dependencies (please report upstream; we track via `pnpm audit` and `pip-audit`).
- DoS via resource exhaustion on public demos.
- Social engineering of the maintainers.

## Security Controls (for auditors)

- **Secret scanning:** `gitleaks` runs pre-commit locally and in CI on every PR.
- **Dependency audit:** `pnpm audit --audit-level=high` gates the frontend build; `pip-audit` / `uv audit` covers the backend.
- **Typed code:** TypeScript in `strict` mode with additional flags (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, etc.). `any` is a lint error.
- **Accessibility lint:** `eslint-plugin-jsx-a11y` violations fail the build (a11y is treated as a correctness concern).
- **Conventional commits + branch naming** enforced by husky pre-commit, commit-msg, and pre-push hooks.
- **No AI attribution** in commits or PRs — commits appear under the author's personal identity.
- **Least-privilege CI:** Workflows specify `permissions: contents: read` and pin action versions by major tag.

## Audit Evidence

Audit-relevant artifacts live under `docs/audit/`. Generated reports (CI run logs, dependency scans) are preserved in GitHub Actions artifacts for the retention period configured in that workflow.
