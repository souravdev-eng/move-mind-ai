# Dependency Management Policy

## Principles

1. **Lockfiles are the source of truth.** `pnpm-lock.yaml` (frontend) and `uv.lock` (backend) are committed and CI installs with `--frozen-lockfile` / `uv sync`.
2. **Pin exact versions for production-critical deps.** Indirect deps follow the lockfile. Upgrades are intentional, not incidental.
3. **High or critical advisories block the build.** `pnpm audit --audit-level=high` is a required CI gate.
4. **Minimum required permissions.** Prefer libraries with tight scopes and active maintenance.

## Adding a new dependency

Before adding, ask:

1. **Is it necessary?** Can we do this with what we already have, or with ~30 lines of code?
2. **Is it maintained?** Check last release date, open security issues, weekly downloads.
3. **What's the license?** MIT / Apache-2.0 / BSD preferred. No GPL/AGPL in the frontend bundle. Unknown/custom licenses require maintainer review.
4. **What's the install footprint?** Check transitive dep count with `pnpm why` / `uv tree`.

Then:

- Add to `dependencies` (runtime) or `devDependencies` / `[project.optional-dependencies].dev` (build/test).
- Commit the updated lockfile **in the same PR**.
- Note in the PR description: why, chosen version, license.

## Upgrading

- **Security advisories:** upgrade immediately, out of the normal cadence. CI audit will fail builds until resolved.
- **Routine upgrades:** monthly pass with `pnpm update --interactive` / `uv lock --upgrade`. One PR per major-version bump so review stays focused.
- **Major bumps** require smoke-testing the impacted surface (build, tests, dev server).
- Do **not** use `--no-audit` or bypass lockfile install flags to work around failures.

## Removing

- Remove the import, remove the dep, update the lockfile. Run `pnpm dedupe` after cluster removals.
- If removing a package used across many files, land the import removal first, then the dep removal in a follow-up PR to keep diffs scoped.

## Third-party review

Before any external audit:

1. Run `pnpm audit --prod` and save the output to `docs/audit/samples/` (redact internal URLs if any).
2. Run `uv tree --depth 2 > docs/audit/samples/uv-tree.txt` for backend visibility.
3. Confirm `CODEOWNERS` has correct ownership for every dep-touching path.
