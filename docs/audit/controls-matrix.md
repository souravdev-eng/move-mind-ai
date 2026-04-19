# Controls Matrix

Snapshot of which security/quality controls exist, where they live, and how they are enforced. Update this whenever a control is added, removed, or materially changed.

| #  | Control                        | Implementation                                                         | Enforcement                                   | Evidence                                |
| -- | ------------------------------ | ---------------------------------------------------------------------- | --------------------------------------------- | --------------------------------------- |
| 1  | Secret scanning                | `gitleaks` + `.gitleaks.toml`                                          | Husky pre-commit (local) + `security-ci.yml` | Action logs; redacted sample in `samples/` |
| 2  | Conventional commits           | `commitlint.config.cjs` + `@commitlint/config-conventional`            | Husky `commit-msg` + `security-ci.yml`       | Action logs                             |
| 3  | Branch naming                  | Regex validated in `.husky/pre-push` + `security-ci.yml`              | pre-push hook + PR CI                         | Action logs                             |
| 4  | TypeScript strictness          | `tsconfig.json` with `strict`, `noUncheckedIndexedAccess`, etc.        | `frontend-ci.yml` → typecheck                 | Action logs                             |
| 5  | ESLint quality gate            | `eslint.config.mjs` (a11y, security, import, no-secrets, TS strict)    | pre-commit (`lint-staged`) + `frontend-ci.yml`| Action logs                             |
| 6  | Accessibility                  | `eslint-plugin-jsx-a11y`                                               | ESLint rule — blocks merge                    | Action logs                             |
| 7  | Prettier formatting            | `.prettierrc.json`                                                     | pre-commit + `frontend-ci.yml` format:check   | Action logs                             |
| 8  | Dependency audit (FE)          | `pnpm audit --audit-level=high`                                        | `frontend-ci.yml` audit job                   | Action logs                             |
| 9  | Dependency audit (BE)          | `uv`/`pip-audit` (to be wired — see `dependency-policy.md`)            | `backend-ci.yml` (planned)                    | TBD                                     |
| 10 | Test quality floor             | Vitest with coverage thresholds (80/80/75/80)                          | `frontend-ci.yml` test job                    | Action logs                             |
| 11 | Least-privilege CI             | `permissions: contents: read` on every workflow                        | Code review                                   | Workflow files                          |
| 12 | CODEOWNERS                     | `.github/CODEOWNERS`                                                    | GitHub branch protection (when enabled)       | File + branch protection rules          |
| 13 | Vulnerability disclosure       | `SECURITY.md`                                                           | Published policy                              | `SECURITY.md`                           |
| 14 | Personal git identity          | Repo-local `user.name` / `user.email`                                  | Manual; memory note for assistants            | `.git/config`                           |
| 15 | No AI attribution              | Policy: no `Co-Authored-By: Claude`, no generated-with footer           | Author discipline + memory note              | Commit log                              |

## Gaps / TODO

- Control #9 (backend audit) is not yet wired in CI. Add `pip-audit` or `uv audit` step to `backend-ci.yml`.
- Branch protection rules on `main` must be enabled in GitHub settings (not code-controlled): require CI green, require review, block force-push.
- No automated SBOM generation yet — add when moving toward productionization.
