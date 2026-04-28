# Frontend Agent Rulebook Index

This folder is the **binding style guide** for all frontend work in `frontend/`. Every rulebook here overrides generic defaults. Claude Code does not auto-load these files from frontmatter — the agent (or a human contributor) MUST open the relevant rulebook before acting on a matching task.

## Task → Rulebook Routing

Use this table to decide which rulebook(s) to load for a given task. Load every file marked "always" plus any task-specific ones.

| Task type                                                    | Rulebooks to load                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------------ |
| **Always (any frontend change)**                             | `architecture.md`, `typescript.md`                                 |
| Creating or editing a component                              | `component-pattern.md`, `styling.md`, `ui_ux.md`                   |
| Writing styles / themes / animations                         | `styling.md`                                                       |
| Working with global state / reducers / context               | `state.md`                                                         |
| Consuming or emitting SSE / streaming UI                     | `streaming.md`, `generative_ui.md`                                 |
| Agent pipeline visualization, live AI output, dynamic render | `generative_ui.md`, `ui_ux.md`                                     |
| Adding or changing tests                                     | `testing.md`                                                       |
| Adding structured logging / metrics / traces                 | `observability.md`                                                 |
| Storybook stories (when installed)                           | `storybook.md`                                                     |
| Reviewing a PR / self-review before commit                   | `code_review.md` (+ every rulebook touched by the diff)            |

## How rules take precedence

1. **Security and accessibility rules are non-negotiable.** If a rulebook conflicts with a "style preference," the stricter rule wins.
2. **Audit posture before ergonomics.** This repo is built to pass third-party audit. If a shortcut would fail audit (hardcoded secret, missing a11y attribute, untyped `any`, inline style bypass), don't take it.
3. **The rulebook is the source of truth.** If a file in `frontend/src/` contradicts a rulebook, the code is wrong — fix it, don't fork the rule.

## When a rulebook is silent

If you encounter a decision the rulebooks don't cover, stop and ask. Don't set a new precedent silently — once a pattern exists it calcifies. Propose the rule, get alignment, then add it to the appropriate rulebook (or create a new one) before writing code.

## Frontmatter note

Each rulebook has `trigger:` and `globs:` frontmatter — this is the Cursor convention, retained for compatibility. It does not drive auto-loading in Claude Code; use the routing table above.
