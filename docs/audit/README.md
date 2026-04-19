# Audit Evidence

This folder holds artifacts used to demonstrate audit posture to third parties. It is deliberately lightweight — the goal is to make a reviewer's first 30 minutes trivial.

## What goes here

| File / folder                        | Purpose                                                                 |
| ------------------------------------ | ----------------------------------------------------------------------- |
| `controls-matrix.md`                 | Map of controls → implementation → evidence location.                   |
| `dependency-policy.md`               | How dependencies are added, pinned, upgraded, and audited.              |
| `threat-model.md` (when ready)       | Data flow diagram + trust boundaries + STRIDE-lite analysis.            |
| `access-review.md` (when ready)      | Who has what access; cadence for review.                                |
| `samples/`                           | Redacted sample outputs (e.g., gitleaks report, pnpm audit output).     |

## What does NOT go here

- Live secrets, credentials, or customer data. Audit samples **must be redacted**.
- Generated reports from CI runs — those live in GitHub Actions artifacts with the workflow's retention policy.
- Anything that duplicates `SECURITY.md` — point to that file instead.

## Keeping this current

- Review `controls-matrix.md` at the start of every quarter.
- Update `dependency-policy.md` whenever the lockfile or upgrade cadence changes.
- Run `gitleaks detect --report-path docs/audit/samples/gitleaks.redacted.json` before any external audit engagement; redact manually before committing.
