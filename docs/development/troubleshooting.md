# Troubleshooting

Common snags and their fixes. If something is broken and not listed here, add it after you fix it.

## Setup

### `pnpm install` warns: "Unsupported engine: wanted Node >= 22"

Your local Node is older. Fix with:

```bash
nvm use               # reads .nvmrc
# or
nvm install 22 && nvm use 22
```

CI uses Node 22 unconditionally (pinned via `.nvmrc` + `actions/setup-node@v4`).

### Husky hooks not running

Symptoms: commits go through without lint, commit-msg check, or branch-name check.

Check:

```bash
git config core.hooksPath
# expected: .husky
```

If empty, re-run the frontend `prepare` script:

```bash
pnpm --prefix frontend run prepare
```

This sets `core.hooksPath=.husky`. The `prepare` lifecycle script runs automatically on `pnpm install`, so a fresh clone should self-configure.

### `gitleaks: command not found` warning in pre-commit

Gitleaks is optional locally. Install it to get the same secret-scanning CI runs:

```bash
brew install gitleaks            # macOS
# or see https://github.com/gitleaks/gitleaks for other platforms
```

If you skip installing it, the pre-commit hook prints a warning and continues. CI will catch secrets before merge regardless.

### `.husky/pre-commit: Permission denied`

Hooks need to be executable:

```bash
chmod +x .husky/pre-commit .husky/commit-msg .husky/pre-push
```

## Committing

### `commit-msg` hook rejects my commit

Message must follow conventional-commits: `<type>(<scope>): <subject>`.

Good: `feat(chat): add streaming token buffer`
Bad: `added new thing` (missing type)
Bad: `FEAT: Added new thing.` (uppercase type, title-case, trailing period)

Full rules: [`workflow.md`](workflow.md#commit-messages).

### `pre-push` hook rejects my branch

Branch name must be `<type>/<kebab-description>`. Rename:

```bash
git branch -m feat/my-proper-branch-name
```

Types allowed: `feat|fix|chore|docs|refactor|test|perf|ci|build|revert|style`. Exempt: `main`, `master`, `develop`, `release/*`, `hotfix/*`.

### My commit was authored under the wrong identity

If it happened on your *last* commit and you haven't pushed:

```bash
git config user.name  "<your personal name>"
git config user.email "<your personal email>"
git commit --amend --reset-author --no-edit
```

If you already pushed, rebase and re-author. If commits are older, ask the maintainer — history rewrites on shared branches need coordination.

## Linting and types

### `'react-hooks/exhaustive-deps' suggested adding X — it causes an infinite loop`

The rule is a **warning**, not an error — it cannot block your build. If the suggestion is wrong:

1. Check whether the dep is stable (`useCallback` result, primitive, ref).
2. If not, memoize it with `useMemo` / `useCallback` and depend on the memoized value.
3. If truly not needed (e.g. mount-only effect), disable with a specific reason:
   ```tsx
   // eslint-disable-next-line react-hooks/exhaustive-deps -- initial fetch only; filters handled by separate effect
   useEffect(() => { fetchOnce(); }, []);
   ```

Full policy: [`agents/frontend/component-pattern.md`](../../agents/frontend/component-pattern.md#hook-dependency-policy-react-hooksexhaustive-deps).

### `@typescript-eslint/no-unnecessary-condition` flags my runtime null-check

The strict-type-checked rules assume types are accurate. This fires when TS believes a value can't be `undefined` / falsy, but the runtime says otherwise (common with browser APIs under jsdom, e.g. `window.matchMedia`).

Two paths:

- **Fix the type.** If TS is wrong, the type declaration is wrong — narrow it.
- **Disable with a reason** if you know the runtime truth:
  ```ts
  // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition -- jsdom does not implement matchMedia
  if (!window.matchMedia) { ... }
  ```

### ESLint import/order errors

Auto-fixable — just run:

```bash
pnpm lint:fix
```

## Tests

### `window.matchMedia is not a function` in tests

jsdom does not ship `matchMedia`. The repo's `src/test/setup.ts` shims it. If a new test env doesn't pick this up, ensure `vitest.config.ts` points `setupFiles` at `./src/test/setup.ts`.

### `An update to X inside a test was not wrapped in act(...)`

React 19 + Testing Library sometimes logs this spuriously when state updates happen during a pending promise. Usually harmless. If it's flaky:

- Wrap user interactions in `await user.click(...)` (userEvent returns a promise).
- Use `await waitFor(() => ...)` for async assertions.

If it's reproducibly breaking tests, open an issue — don't silence with `vi.spyOn(console, 'error')`.

### Coverage fails at 79.x%

Thresholds are 80/80/75/80 (stmts/funcs/branches/lines). Missing coverage almost always means an **untested branch** — an error path, a conditional render, or a reducer case. Run `pnpm test:coverage` locally and open `coverage/index.html` to see exactly which lines are red.

## CI

### `frontend-ci / quality` fails but passes locally

Common causes:

- **Node version drift.** Did you upgrade `.nvmrc` or lockfile without bumping the other?
- **Platform-specific code.** Path separators, locale, or `window` access leaking to SSR. Check the failing job log.
- **Stale cache.** Clear the action cache from GitHub UI and rerun.

### `security-ci / gitleaks` flags a file

It detected something that looks like a secret (high-entropy string, API key pattern). Options:

1. **It's a real secret:** remove it, rotate the credential, force-push the cleaned history, email `souravmajumdar.developer@gmail.com` immediately.
2. **It's a false positive:** add a narrow allowlist entry to `.gitleaks.toml` with a comment explaining why. Do not widen allowlists to silence the scanner.

### `pnpm audit` fails on a new advisory

- **Direct dep:** upgrade to the patched version, or remove the dep.
- **Transitive dep:** use `pnpm up --depth Infinity <package>` to force resolution; if no patched version exists upstream, `pnpm.overrides` in `package.json` is the last resort (document the override).
- Never bypass the audit gate with `--audit-level=none`.

## When in doubt

- Re-read [`../../CLAUDE.md`](../../CLAUDE.md) — it's the source of truth for tooling and conventions.
- Check the relevant rulebook in [`agents/frontend/`](../../agents/frontend/).
- Open an issue with the `question` label.
