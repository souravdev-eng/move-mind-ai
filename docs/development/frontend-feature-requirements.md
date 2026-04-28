# MoveMind AI — Frontend Feature Requirements (v2 SaaS UI)

> Version: 0.1 (Draft)
> Date: 2026-04-19
> Source of truth: [docs/sow.md](../sow.md) v1.1
> Scope: UI/UX feature requirements for the v2 SaaS web app — information architecture, navigation, onboarding, per-project workspace, and integrations (Jira, Notion, MCP, log connectors).

---

## Table of Contents

1. [Purpose & Guiding Principles](#1-purpose--guiding-principles)
2. [User Roles & Primary Jobs](#2-user-roles--primary-jobs)
3. [Information Architecture](#3-information-architecture)
4. [Navigation Model](#4-navigation-model)
5. [Onboarding Flow (Org → Project → First Question)](#5-onboarding-flow-org--project--first-question)
6. [Page-by-Page Requirements](#6-page-by-page-requirements)
7. [Integrations Hub](#7-integrations-hub)
8. [MCP Server Connector (Dedicated)](#8-mcp-server-connector-dedicated)
9. [Conversation / Chat Workspace](#9-conversation--chat-workspace)
10. [Descriptor Management UI](#10-descriptor-management-ui)
11. [Observability & Billing Surfaces](#11-observability--billing-surfaces)
12. [Cross-Cutting UX Requirements](#12-cross-cutting-ux-requirements)
13. [Phasing (MVP → GA)](#13-phasing-mvp--ga)
14. [Open UI Decisions](#14-open-ui-decisions)

---

## 1. Purpose & Guiding Principles

The frontend must make the SOW promise concrete: *"you connect your logs, we understand your system"*. A technical user must go from sign-up → live project → answered question in **under 5 minutes** (SOW §9).

Principles:

1. **Project is the center of gravity.** Everything the user sees is scoped to the active project (descriptor, logs, conversations, integrations). Org-level views are secondary.
2. **Self-serve, no hand-holding.** Every onboarding, connector, and integration step must be completable without contacting MoveMind.
3. **Honest uncertainty.** Profiler confidence, code-context recall, schema drift — all surfaced, never hidden.
4. **Audit-grade defaults.** Accessibility, strict TS, no secrets in client code — per project CLAUDE.md.
5. **Streaming-first.** Agent responses, ingestion progress, connector syncs all render incrementally.
6. **Manager vs developer modes are a first-class toggle**, not a setting buried in preferences.

---

## 2. User Roles & Primary Jobs

| Role | Primary jobs in the UI |
| --- | --- |
| **Org admin** | Create org, invite members, manage billing, set retention & PII policy |
| **Project owner** | Create project, configure connector, confirm descriptor, manage integrations |
| **Engineering lead** | Ask investigative questions, review timelines, create Jira tickets |
| **Manager / non-technical** | Ask plain-English questions, read verdict (bug vs business condition), share/export |
| **Developer (ticket recipient)** | Consume Jira/Notion output; optionally click deep-link back into the investigation |

Role permissions are RBAC-driven; UI chrome hides actions the role cannot perform rather than disabling them visibly (except for billing, which always shows a contact-admin CTA).

---

## 3. Information Architecture

```
Org (tenant boundary)
├── Dashboard (org-wide health)
├── Projects
│   └── {project}
│       ├── Overview
│       ├── Conversations (chat history)
│       ├── Investigate (new chat)
│       ├── Logs
│       │   ├── Connectors
│       │   ├── Ingestion Runs
│       │   └── Schema / Descriptor
│       ├── Integrations
│       │   ├── Jira
│       │   ├── Notion
│       │   ├── Slack (post-MVP)
│       │   └── Webhooks (outbound)
│       ├── Code Context
│       │   ├── MCP Servers
│       │   └── Hosted Repo Index
│       ├── Evaluations (quality dashboard)
│       └── Settings (members, retention, danger zone)
├── Integrations (org-level templates & secrets)
├── Members & Roles
├── Billing & Usage
└── Account (personal preferences)
```

---

## 4. Navigation Model

Three-level nav, consistent across the app:

1. **Top bar (global):** Org switcher • Project switcher (search + recents) • Global search (⌘K) • Notifications • Account menu.
2. **Left rail (project-scoped primary nav):** Overview, Investigate, Conversations, Logs, Integrations, Code Context, Evaluations, Settings. Collapsible on small viewports.
3. **Sub-nav (nested, context-sensitive):** Rendered as secondary tabs inside the left rail section. Example: `Logs → [Connectors | Ingestion Runs | Schema]`. Integrations and Code Context use the same nested pattern — **one page per integration** beneath the section root.

Rules:

- URL is the source of truth: `/orgs/{orgId}/projects/{projectId}/logs/connectors`. Every nested page is deep-linkable and shareable.
- Breadcrumbs show Org → Project → Section → Sub-section and are always clickable.
- Switching projects preserves the current section (e.g. if you were on *Integrations → Jira* for Project A, switching to Project B lands you on *Integrations → Jira* for B).
- Global ⌘K palette supports: jump to project, jump to conversation, create project, create ticket, open descriptor, run eval.

---

## 5. Onboarding Flow (Org → Project → First Question)

Mapped directly to SOW §5 experience steps.

### 5.1 Org creation (first run only)

- Create org (name, slug, timezone, billing email).
- Invite teammates (optional, skippable).
- Pick starter plan (trial by default).

### 5.2 Create Project wizard (multi-step, resumable)

| Step | UI |
| --- | --- |
| 1. Project basics | Name, slug, short description, icon/color |
| 2. Connect a log source | Gallery of connectors: **File Upload, S3, CloudWatch, Webhook, Datadog, Elastic, Kafka** (availability gated per phase). Each card shows status: `Available | Beta | Coming soon` |
| 3. Configure connector | Per-connector form (creds, bucket/log group, filters). Live **Test Connection** button with streamed output |
| 4. Pull sample | Fetch 200–1000 events. Progress bar with live event counter |
| 5. Profiler review | Descriptor form pre-filled by Profiler Agent (see §10) |
| 6. Confirm & ingest | Kick off full ingestion job; user can leave the page — progress shown in top bar toast + Ingestion Runs page |
| 7. Ready | Land on **Investigate** with a suggested starter question from the profiler's sample questions |

Requirements:

- Wizard state is persisted server-side; user can close the tab and resume from the project card.
- Every step is individually re-enterable from Logs section after the project is live.
- "Skip connector, upload a file" escape hatch always present (reference project parity with v1 CMS3 flow).

### 5.3 Empty-state cues

- Before a connector is attached: project Overview explains what to do next with a 3-step checklist.
- Before first question: Investigate shows suggested questions derived from the descriptor vocabulary.

---

## 6. Page-by-Page Requirements

### 6.1 Org Dashboard

- KPI strip: projects count, active connectors, ingestion events last 24h, unresolved drift alerts, spend-to-date.
- Per-project health table: connector status, last sync, last ingestion error, last eval score.
- Recent conversations across projects (role-filtered).

### 6.2 Project Overview

- Descriptor summary card (domain_id, display_name, primary correlation key, vocabulary chips) — click to open full descriptor.
- Health tiles: connector sync freshness, ingestion success rate (7d), eval score trend, P95 answer latency, open drift alerts.
- Recent conversations (project-scoped).
- "Ask a question" quick-launch → Investigate with prefilled input.

### 6.3 Investigate (new chat)

See §9.

### 6.4 Conversations

- List view with filters: author, date range, verdict (`bug | business_condition | unknown`), has-ticket, has-code-context.
- Columns: title, last message preview, verdict badge, created_at, participants.
- Row click → open conversation in read-only mode with a "Continue" button that forks a new thread.
- Bulk actions: export (CSV/JSON), archive, link to Notion page.

### 6.5 Logs → Connectors

- One row per connector with: type icon, status (`Healthy | Warning | Failed`), last sync, next scheduled sync, events ingested last 24h, actions (Pause, Sync now, Edit, Delete).
- "Add connector" opens the same gallery as onboarding step 2.

### 6.6 Logs → Ingestion Runs

- Timeline of ingestion jobs (manual uploads + scheduled syncs).
- Each run: started, duration, events in/out (post-filter), embed cost, errors count.
- Expand a run → event-level error log, re-run button (idempotent where possible).

### 6.7 Logs → Schema / Descriptor

See §10.

### 6.8 Evaluations

- Project eval score trend (Ragas faithfulness, answer relevance, classify_issue coverage).
- Golden dataset view (read-only for non-owners; add/edit for owners).
- "Run eval" button (rate-limited); last N runs with diff-vs-baseline badge.
- Surfaces the SOW §9 metrics: faithfulness ≥ 0.85, classify_issue 100%, P95 latency < 10s.

### 6.9 Project Settings

- Members & roles (RBAC per project).
- Retention policy (conversations, raw logs) — governed by org policy but overridable if allowed.
- Danger zone: re-profile, rotate namespace, delete project (type-to-confirm).

### 6.10 Org → Members & Roles

Standard RBAC admin: invite, role assignment (Admin, Owner, Member, Viewer), SCIM (post-GA).

### 6.11 Org → Billing & Usage

- Usage meters per SOW §9: events ingested, questions asked, tokens in/out, Pinecone vector storage, MCP calls.
- Per-project cost breakdown.
- Plan management + invoice history (Stripe/Lago TBD per SOW §11).

### 6.12 Account

Personal: name, email, password, 2FA, default explanation mode (manager vs developer), theme, API tokens (post-GA).

---

## 7. Integrations Hub

Integrations exist at two levels:

- **Org-level** (`/orgs/{orgId}/integrations`): shared credential vault & templates — e.g. a Jira site connected once, reusable across projects.
- **Project-level** (`/orgs/{orgId}/projects/{projectId}/integrations`): per-project activation, mapping, and rules.

### 7.1 Integrations gallery (common pattern)

Each integration is a card with: logo, name, one-line pitch, status (`Not connected | Connected | Needs attention`), category chip (`Ticketing | Docs | Chat | Code | Alerting | Connector`). Clicking opens that integration's dedicated page (nested sub-nav).

### 7.2 Jira integration page

- **Connect:** OAuth to Atlassian site → select Jira projects allowed → set default issue type & priority mapping.
- **Mapping:** Map MoveMind verdict → Jira labels/components; pick which fields populate from the technical report & steps-to-reproduce (SOW Phase 0 P-05/06/07).
- **Triggering rules:** Manager-triggered-only (per SOW §10 "out of scope" — no auto-create).
- **Activity tab:** List of tickets created from this project with deep links.
- **Test:** "Create test ticket" button (writes to a chosen sandbox project).

### 7.3 Notion integration page

- **Connect:** Notion OAuth → select workspace & target parent page/database.
- **Templates:** Map investigation output to a Notion page template (fields: verdict, timeline, evidence, code references).
- **Auto-publish rules:** Optional — e.g. "publish to Notion when verdict = bug AND ticket created".
- **Activity tab:** Pages published from this project; backlink to original conversation.

### 7.4 Slack (post-MVP)

- Channel routing per verdict; digest vs per-event.

### 7.5 Outbound webhooks

- Generic `POST` on `investigation.completed`, `ticket.created`, `drift.detected` events; HMAC-signed. Delivery log with replay.

### 7.6 Log-source connectors

Treated as a sibling concept under **Logs → Connectors** (not under Integrations), because their semantics differ (ingestion pipeline, not output). The UI must make this distinction obvious via iconography and left-rail grouping.

---

## 8. MCP Server Connector (Dedicated)

MCP is significant enough to warrant its own section under **Code Context**, with its own nested pages. Rationale: MCP is the v2 story for code grounding (SOW §6) and has a different mental model than data-source or output integrations.

### 8.1 `Code Context → MCP Servers`

- **List view:** connected MCP servers for this project. Columns: name, transport (stdio / HTTP / SSE), URL/command, status (`Connected | Handshaking | Error`), last heartbeat, exposed tools count, exposed resources count.
- **Add server flow:**
  1. Choose transport (stdio for local/self-hosted, HTTP/SSE for remote).
  2. Enter endpoint + auth (OAuth, bearer, or mTLS).
  3. MoveMind performs `initialize` handshake and streams the tool/resource list back to the UI.
  4. User whitelists which tools the agent may call (e.g. `get_code_context`, `get_recent_changes`) and which resources are readable.
  5. Scope: read-only by default; any write-capable tool requires explicit per-tool opt-in with a warning.
- **Per-server detail page:** tools tab (name, description, input schema, last call stats), resources tab (URI templates, last read), invocation log (recent tool calls with input/output previews — secrets redacted), health (latency, error rate), danger zone (revoke, rotate token).

### 8.2 `Code Context → Hosted Repo Index` (fallback)

Per SOW §6 option 2 — when the user has no MCP server:

- Connect GitHub/GitLab/Bitbucket via OAuth (read-only scope).
- Pick repos to index; show index size + estimated cost.
- Incremental re-index on push (webhook).
- Surface the same `get_code_context` tool to the agent but backed by MoveMind's index.

### 8.3 Code Context usage in chat

When the agent calls an MCP tool during an investigation, the chat transcript must show an inline, collapsible "Tool call" block with: tool name, server, input, output snippet, latency. This is part of the honest-uncertainty principle (SOW C-06).

---

## 9. Conversation / Chat Workspace

The primary workspace after onboarding.

### 9.1 Layout

Three-pane responsive layout:

- **Left:** scope panel — active correlation key input (e.g. CID, customer_id), time window, explanation mode toggle (Manager ↔ Developer), descriptor summary peek.
- **Center:** streaming chat transcript.
- **Right (collapsible):** evidence drawer — retrieved log chunks, timeline view, code context hits, tool call log.

### 9.2 Message affordances

- Agent messages stream token-by-token (SSE, matching backend `/api/v2/.../chat`).
- Tool calls render inline (see §8.3).
- Every factual claim links to the evidence item(s) in the right drawer.
- Verdict badge appears once `classify_issue` completes (guaranteed by backend post-processing guard, SOW C-10). If missing after N seconds, show a "Classifying…" state — never an empty state.
- Per-message actions: copy, share link, create Jira ticket, publish to Notion, rate (👍/👎 feeds eval).

### 9.3 Timeline view

- Toggle in the right drawer. Chronological list of events within the current scope, grouped by descriptor's `group_by` keys. Honors descriptor vocabulary (e.g. "journey", "step").

### 9.4 Clarify-with-user

- When the agent calls `clarify_with_user`, it renders as a structured prompt (not free text) with suggested answers where possible.

### 9.5 Ticket creation (manager flow)

- Manager mode exposes a prominent "Create Jira ticket" CTA once a verdict is produced.
- Opens a modal with the technical report + steps-to-reproduce pre-filled (Phase 0 P-05/06/07). User edits → submits → link appears inline.

---

## 10. Descriptor Management UI

### 10.1 Descriptor form (onboarding + edit)

Fields grouped per SOW §5 YAML:

- **Identity:** `domain_id`, `display_name`.
- **Correlation & grouping:** `correlation_keys.primary`, `.secondary`, `group_by[]`.
- **Identifiers:** actor, flow, unit, location.
- **Timing & levels:** `timestamp_field`, `level_field`, `message_field`.
- **Error signals:** fields + level values.
- **Vocabulary:** event_unit, flow_unit, actor_unit, routing_unit (free text with autocomplete suggestions from the profiler).
- **Known patterns:** editable multiline list.
- **Domain description:** long-form textarea.

Per field:

- **Confidence indicator** (🟢/🟡/🔴) from the profiler.
- **Source snippet** ("inferred from 47/200 events") on hover.
- **Override** control, persisted with an `edited_by_user: true` flag.

### 10.2 Live preview

- Right panel shows one real execution group reconstructed using the current descriptor. Changes re-render the preview instantly.

### 10.3 Versioning

- Each save creates a new descriptor version; ingestion pins to a version (SOW C-07).
- Diff view between versions.
- "Re-profile" action (with warning about re-ingestion cost).

### 10.4 Drift alerts

- Banner on the descriptor page when drift detector flags new unknown fields > 10% of recent events. One-click "Re-profile sample" CTA.

---

## 11. Observability & Billing Surfaces

- **Org Dashboard** + **Project Overview** expose the SOW §9 metrics (eval scores, latency, connector sync success, classify_issue coverage) using sparklines.
- **Billing & Usage** shows per-meter consumption (events ingested, questions, tokens, vector storage, MCP calls) with projected monthly spend.
- **Cost guardrails:** admin-settable soft caps that trigger in-app warnings before hard caps pause ingestion.

---

## 12. Cross-Cutting UX Requirements

Derived from CLAUDE.md + SOW principles; these are non-negotiable.

- **Accessibility:** WCAG 2.1 AA. Keyboard-navigable throughout, visible focus rings, ARIA on custom widgets. `jsx-a11y` passes in lint.
- **Strict TypeScript:** no `any`; all API payloads typed via shared contract (e.g. generated from OpenAPI).
- **Streaming:** every long-running op (ingestion, agent answer, connector test, MCP handshake) renders progress; no silent spinners > 3s.
- **Error states:** every page has empty / loading / error / partial-data variants designed upfront, not retrofitted.
- **Multi-tenancy safety:** the active project is displayed in persistent chrome; destructive actions include project name as type-to-confirm.
- **Secrets:** credential fields are write-only from the client's perspective (mask-on-read); rotation UI surfaces `last_rotated_at`.
- **PII:** any sample log preview in onboarding or descriptor UI goes through server-side PII scan first (SOW C-04, Phase 3).
- **Theming:** light + dark. No brand-only colors for state (use shape + color + label).
- **i18n-ready:** no hardcoded strings in components; design for English-first but don't block localization.
- **Telemetry:** client-side page-view and interaction events routed through a single wrapper; no third-party analytics SDKs without review.

---

## 13. Phasing (MVP → GA)

Aligned with SOW Phase 2/3/4.

### MVP (SOW Phase 2–3, ~12–16 weeks of FE work)

- Auth, Org/Project model, Project switcher.
- Onboarding wizard with File Upload + S3 + Webhook connectors.
- Descriptor form + live preview + versioning.
- Investigate chat workspace (streaming, evidence drawer, verdict badge).
- Conversations list + detail.
- Logs → Connectors, Ingestion Runs, Schema.
- Integrations: Jira (manager-triggered ticket creation).
- MCP Servers page (connect, tool whitelist, invocation log).
- Evaluations read-only view.
- Billing & usage meters.

### Fast-follow (SOW Phase 4)

- Notion integration.
- CloudWatch, Datadog connectors.
- Hosted Repo Index fallback (for no-MCP users).
- Outbound webhooks.
- Slack integration.
- Schema drift alerting UI.

### Post-GA

- Public API tokens UI, SCIM, advanced RBAC, saved investigations/playbooks, shared dashboards, self-hosted admin console.

---

## 14. Open UI Decisions

Parallel to SOW §11; these need Product+Eng alignment before build.

| Decision | Options | Target |
| --- | --- | --- |
| Component library depth | MUI-only vs MUI + bespoke primitives layer | Before MVP kickoff |
| Chat transcript virtualization | react-window vs MUI native vs custom | Before Investigate build |
| Evidence drawer density | Always-visible vs overlay vs tabbed | Design review |
| Descriptor form layout | Single long form vs stepper vs split-pane with live preview | After profiler prototype |
| MCP tool whitelist UX | Per-tool toggle vs role-style bundles | Before MCP GA |
| Notion template authoring | In-app template editor vs link-to-Notion template | Post-Jira ship |
| Global search (⌘K) scope | Org-wide vs project-scoped default | Before MVP |
| Theme | Light-first / dark-first / system | Design review |

---

_This document is the FE counterpart to `docs/sow.md`. It should be revised alongside any SOW revision and before each phase kickoff. The next artefact to produce from this is a low-fidelity wireframe set for the MVP pages in §13._
