# Code Style

This doc is a **map**, not a catalogue. The actual rules live in the ESLint config, the TypeScript config, and the `agents/frontend/*` rulebooks. This doc tells you where to look and summarizes the guiding principles.

## Guiding principles (repo-wide)

1. **Audit-readiness over ergonomics.** Shortcuts that fail audit never ship. If it's easier to do the wrong thing, the tooling is wrong — fix the tooling.
2. **Types and tests are correctness tools.** `any`, `// @ts-ignore`, and untested branches are not stylistic choices — they are defects.
3. **Rules are enforced, not implied.** Every convention here has a linter, hook, or CI gate behind it. Documentation is secondary.
4. **Delete over comment.** Dead code rots. If it's unused, remove it — git remembers.
5. **Don't invent conventions silently.** If the rulebooks don't cover your situation, propose the rule in a PR before landing code that sets a new precedent.

## Frontend

### Rulebook routing

`agents/frontend/` is the binding style guide. Start at [`agents/frontend/README.md`](../../agents/frontend/README.md) and follow the routing table:

| Task                                  | Rulebook(s)                                         |
| ------------------------------------- | --------------------------------------------------- |
| Any frontend change (always)          | `architecture.md`, `typescript.md`                  |
| Creating/editing a component          | `component-pattern.md`, `styling.md`, `ui_ux.md`    |
| Styles, themes, animations            | `styling.md`                                        |
| Global state / reducers / context     | `state.md`                                          |
| SSE / streaming / live AI output      | `streaming.md`, `generative_ui.md`                  |
| Tests                                 | `testing.md`                                        |
| Logging / metrics / traces            | `observability.md`                                  |
| PR self-review                        | `code_review.md`                                    |

### TypeScript

Configured in [`frontend/tsconfig.json`](../../frontend/tsconfig.json). Non-default flags turned on:

- `strict` (all strict mode checks)
- `noUncheckedIndexedAccess` — array/object index access returns `T | undefined`
- `exactOptionalPropertyTypes` — `foo?: string` is not the same as `foo: string | undefined`
- `noImplicitOverride` — must mark overrides explicitly
- `noPropertyAccessFromIndexSignature` — no `obj.foo` on index-signature types, use `obj["foo"]`
- `verbatimModuleSyntax` — import syntax must match intent (`import type` for types)

**Rule of thumb:** if TypeScript complains, assume it is right. If you truly need to escape, use a narrowing cast with a comment explaining why — `// @ts-ignore` is banned, `// @ts-expect-error` requires a ≥ 10-char description.

### ESLint

Configured in [`frontend/eslint.config.mjs`](../../frontend/eslint.config.mjs). Layers:

1. `@typescript-eslint` `strictTypeChecked` + `stylisticTypeChecked`
2. `eslint-plugin-react` + `react-hooks`
3. `eslint-plugin-jsx-a11y` (accessibility — non-negotiable)
4. `eslint-plugin-import` (order, cycles, duplicates)
5. `eslint-plugin-security` (basic security smells)
6. `eslint-plugin-no-secrets` (entropy-based secret detection)

### `react-hooks/exhaustive-deps`

Set to `warn`, never `error`. Why: its suggestions are frequently wrong for memoized callbacks and refs; making it an error would push devs to auto-fix into infinite loops.

**How to handle a warning:** see [`agents/frontend/component-pattern.md`](../../agents/frontend/component-pattern.md#hook-dependency-policy-react-hooksexhaustive-deps). Short version: verify correctness, then either add the dep, memoize the value, or disable with a specific reason: `// eslint-disable-next-line react-hooks/exhaustive-deps -- <one-line invariant>`.

### Prettier

Configured in [`frontend/.prettierrc.json`](../../frontend/.prettierrc.json). No debates — run `pnpm format` and move on.

### Styling (MUI)

- **Never hardcode colors, spacing, font sizes, or radii.** Consume via the MUI theme (`theme.palette.*`, `theme.spacing(n)`, etc.).
- Styles go in `ComponentName.style.tsx`, not inline `sx={{ ... }}` (inline is allowed for one-off layout helpers).
- Light and dark themes must both render cleanly. Verify both before landing a styling change.

Full rules: [`agents/frontend/styling.md`](../../agents/frontend/styling.md).

### Testing

- Vitest + Testing Library for unit/integration.
- Coverage thresholds: **lines ≥ 80, functions ≥ 80, branches ≥ 75, statements ≥ 80**. CI enforces via `pnpm test:coverage`.
- Test the user-observable behavior, not implementation details. Prefer `getByRole` over `getByTestId`.
- SSE streams mocked via `ReadableStream` — patterns in [`agents/frontend/testing.md`](../../agents/frontend/testing.md).

### File and symbol naming

| Thing                            | Convention                          | Example                    |
| -------------------------------- | ----------------------------------- | -------------------------- |
| Component file                   | `PascalCase.tsx`                    | `ChatInput.tsx`            |
| Component style file             | `PascalCase.style.tsx`              | `ChatInput.style.tsx`      |
| Component-local hook             | `PascalCase.hook.tsx`               | `ChatInput.hook.tsx`       |
| Shared hook                      | `useCamelCase.ts`                   | `useSSEStream.ts`          |
| Shared type                      | `types.ts` or domain-specific       | `interfaces/types.ts`      |
| Shared util                      | `kebab-case.ts`                     | `format-message.ts`        |
| React component export           | `PascalCase`                        | `export function ChatInput` |
| Hook export                      | `useCamelCase`                      | `export function useChat`  |
| Type export                      | `PascalCase`                        | `export interface Message` |

## Backend

See [`../../backend/docs/features/`](../../backend/docs/features/) for per-feature teaching docs.

### Python

- **Version:** 3.13 (see `backend/pyproject.toml`).
- **Linter + formatter:** `ruff` — one tool, no debates. Run `uv run ruff check .` and `uv run ruff format .`.
- **Imports are absolute.** From any backend file: `from app.x.y import z`. Runtime root is `backend/`.
- **Config lives in one place.** Use `app.config.Settings` — never call `os.getenv` directly in app code.
- **Model tiers by capability, not vendor.** `OPENAI_FAST`, `OPENAI_SMART`, `OPENAI_THINKING` — pick the tier appropriate to the node.

### Testing

- Pytest; tests mirror `app/` layout under `backend/tests/`.
- Integration tests requiring live APIs are marked `@pytest.mark.integration`. Default CI run excludes them (`-m "not integration"`).

### LangGraph nodes

- State transitions only via `GraphState` fields — nodes return partial dict updates, never mutate.
- Node names are centralized in `app/graphs/constants.py`. Use the constants, not strings.
- Control flow belongs in graphs, not chains. Chains are stateless prompt→LLM→parser.

## Commits and branches

See [`workflow.md`](workflow.md) for the full rules. Summary:

- **Branch:** `<type>/<kebab>` where type ∈ `feat|fix|chore|docs|refactor|test|perf|ci|build|revert|style`.
- **Commit:** `<type>(<scope>): <subject>` — conventional-commits.
- **PR title:** same as commit — CI validates it.

## Dependencies

- **Frontend:** pnpm. Lockfile committed. Add deps with `pnpm add` (runtime) or `pnpm add -D` (dev). See [`../audit/dependency-policy.md`](../audit/dependency-policy.md) for the audit rules.
- **Backend:** uv. Lockfile committed. Add deps with `uv add` (runtime) or `uv add --dev`.

## Documentation style

- **Per-feature teaching docs** in `backend/docs/features/`: pain → mental model → trade-offs → FAQ. Not reference summaries.
- **Contributor docs** in `docs/development/` (you are here): map → rules → examples. Link outward, don't duplicate.
- **Audit docs** in `docs/audit/`: factual, evidence-backed, reviewer-friendly.
- **CLAUDE.md**: agent instructions. Keep it current when conventions shift.
