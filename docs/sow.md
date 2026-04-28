# MoveMind AI — Statement of Work (SOW)

> Version: 1.1  
> Date: April 2026  
> Status: Draft — reviewed and updated  
> Scope: Product vision, architecture direction, phased delivery plan, and key challenges for evolving MoveMind from a CMS3-specific log debugger into a generic, multi-tenant SaaS product.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision](#3-product-vision)
4. [Current State — MoveMind v1](#4-current-state--movemind-v1)
5. [Target State — MoveMind v2 (SaaS)](#5-target-state--movemind-v2-saas)
6. [Architecture Overview](#6-architecture-overview)
7. [Phased Delivery Plan](#7-phased-delivery-plan)
8. [Key Challenges](#8-key-challenges)
9. [Success Metrics](#9-success-metrics)
10. [Out of Scope](#10-out-of-scope)
11. [Open Decisions](#11-open-decisions)

---

## 1. Executive Summary

MoveMind AI is an intelligent log-debugging assistant. Today it is purpose-built for CMS3 — a single application with tightly coupled ingestion logic, prompts, state fields, and retrieval rules. It works well for that problem.

The goal of this SOW is to define the path from that working, narrow tool into a **multi-tenant SaaS product** where any engineering team can onboard their application, connect their log sources, and immediately get an AI assistant that understands their specific system — without MoveMind engineers writing per-customer code.

The core thesis: **the agent logic stays generic and constant; the per-application knowledge lives in a user-confirmed descriptor that drives everything downstream.**

---

## 2. Problem Statement

### The current limitation

Every component of MoveMind v1 is CMS3-specific:

| Layer | CMS3 coupling |
| --- | --- |
| `app/rag/preprocessing.py` | Hardcoded fields: `journey_id`, `execution_id`, `customer_id`, `step_order`, `decision_result`, `page_path` |
| `app/rag/retrieval.py` | `CID_PATTERN` / `PAGE_PATTERN` / `EXECUTION_PATTERN` regexes; `build_api_timeline_documents()` hardcodes `graphql_request` and `gql_*` action patterns; `_sorted_event_docs()` sorts by CMS3-specific `step_order` + `page_path`; `lru_cache(maxsize=1)` on `_processed_chunk_docs()` is a **singleton that returns the same data regardless of project** — silent multi-project failure |
| `app/rag/ingestion.py` | `verify_vectorstore()` contains a hardcoded CMS3 test query (`CID 7093495`); uses `settings.PINECONE_NAMESPACE` and `settings.PROCESSED_CHUNKS_PATH` singletons |
| `app/config.py` | `PINECONE_NAMESPACE = "cms3-logs"`, `RAW_LOGS_PATH`, `PROCESSED_CHUNKS_PATH` are all hardcoded CMS3 paths — no per-project concept exists anywhere in config |
| `app/graphs/nodes/resolve_context.py` | CMS3 API view logic (transport-level vs named GraphQL operations), `analysis_mode="api_calls"` |
| `app/graphs/nodes/generate_answer.py` | Imports `CMS3_CONTEXT_SCHEMA`, hardcodes GraphQL clarification logic |
| `app/graphs/state.py` | State fields: `active_customer_id`, `active_page_path`, `api_view`, `requested_api_count` |
| `app/prompts/templates.py` | `_REWRITE_PROMPT` names "CMS3" and "CID" explicitly; `_MANAGER_ANSWER_PROMPT` says "CMS3 customer journey"; `_DEVELOPER_ANSWER_PROMPT` hardcodes `graphql_request`/`gql_*` rules; `CMS3_CONTEXT_SCHEMA` constant exported and used in `generate_answer` |

Adding a second application (Voyager, Payments, etc.) would require duplicating and modifying all six layers. After 3–5 applications, this collapses into unmaintainable per-customer engineering.

### The business consequence

Without a generic architecture, MoveMind cannot become a SaaS product. Every new customer requires an engineer. The unit economics never work. The product does not scale.

---

## 3. Product Vision

### The one-line statement

> **MoveMind AI is the AI debugging co-pilot for any engineering team — you connect your logs, we understand your system.**

### Who it's for

| User | Role | What they need |
| --- | --- | --- |
| **Manager / Non-technical lead** | Primary user today (CMS3) | Plain English explanation of what went wrong and why, without needing to read logs |
| **Engineering lead** | Primary user for generic SaaS | Fast root cause analysis across log sources without context switching |
| **Developer** | Receives output (Jira tickets) | A fully formed ticket with root cause, evidence, and steps to reproduce |

### The product experience (end state)

```
1. Sign up → Create Organisation
2. Create Project ("CMS3", "Voyager", "Payments Service"...)
3. Connect a log source (file upload / S3 / CloudWatch / webhook)
4. Upload a sample → Profiler Agent auto-detects schema
5. Review + confirm the descriptor form (< 2 minutes)
6. Project is live — start asking questions
7. Optional: connect MCP codebase for code context grounding
8. Optional: set up scheduled sync so logs stay fresh automatically
```

Once onboarded, every project gets the same agent loop — the same intelligence — personalised to their application's schema and vocabulary.

### Core principles

1. **Zero per-customer code.** Onboarding a new application must not require a MoveMind engineer to write code.
2. **Descriptor-driven, not code-driven.** Per-application knowledge lives in a YAML descriptor confirmed by the user — not in Python classes.
3. **Self-serve from day one.** A technical user should be able to onboard their project without talking to anyone at MoveMind.
4. **CMS3 as the reference project.** CMS3 is the first project onboarded using the generic architecture. When MoveMind v2 answers CMS3 questions as well as v1, the architecture is proven.
5. **Agent loop + tools, not a fixed graph.** The rigid `classify → retrieve → rerank → generate` pipeline is replaced by a tool-calling agent that decides its own investigation path, guided by the descriptor.
6. **Code context is a first-class tool, not a bolt-on.** Via MCP or direct repo indexing, code context is one more tool the agent can call. It works for any application, not just CMS3.

---

## 4. Current State — MoveMind v1

### What exists and works well

| Component | Location | Strength |
| --- | --- | --- |
| RAG-based log debugging | `app/graphs/agent.py` | End-to-end working for CMS3 |
| Hybrid retrieval (dense + BM25) | `app/rag/retrieval.py` | Good context coverage per CID |
| FlashRank reranking | `app/chains/reranker_chain.py` | Reduces noise in retrieved context |
| Multi-turn session memory | `app/graphs/state.py` + MemorySaver | Carries context across turns |
| Execution summary + event chunks | `app/rag/preprocessing.py` | Two-layer chunking strategy |
| SSE streaming | `app/api/routes/chat.py` | Real-time token delivery |
| Multi-model routing | `app/utils/helpers.py` | fast / smart / thinking presets |
| LangSmith observability | `app/obs/` | Full trace + cost tracking |
| Eval pipeline | `app/eval/` | Regression gate + golden dataset |
| Issue classification | `app/graphs/nodes/classify_issue.py` | Bug vs. business condition |
| Manager / developer explanation modes | `explanation_mode` in state | Audience-aware output |

### What is missing in v1

Tracked in detail in `docs/tracking/system-audit.md`. Summary:

| Gap                                         | Priority |
| ------------------------------------------- | -------- |
| Structured intake (CID + log upload via UI) | High     |
| Real-time / on-demand log ingestion         | High     |
| Jira ticket creation                        | High     |
| Steps to reproduce generator                | High     |
| Issue persistence (database)                | Medium   |
| Issue deduplication + fingerprinting        | Medium   |
| Generic multi-app support                   | This SOW |

### v1 architecture (current)

```
User question (free text)
        ↓
POST /api/v1/chat
        ↓
LangGraph fixed graph:
  classify_question   → retrieve | rewrite
  rewrite_question    → fix follow-ups using history
  resolve_context     → extract CID, execution_id, page_path (CMS3-specific)
  retrieve_docs       → Pinecone hybrid search
  rerank_docs         → FlashRank top-5
  generate_answer     → gpt-4o with CMS3 context schema
  classify_issue      → bug | business_condition | unknown
        ↓
Answer + sources (SSE streaming)
```

---

## 5. Target State — MoveMind v2 (SaaS)

### Multi-tenancy model

```
Organisation (billing boundary)
  ├── Project: CMS3
  │     ├── descriptor.v1 (auto-generated + confirmed)
  │     ├── Pinecone namespace: org_17_cms3
  │     ├── Connector: S3 (scheduled sync, every 30m)
  │     ├── MCP: github.com/acme/cms3 (read-only)
  │     └── Conversations: [...]
  ├── Project: Voyager
  │     ├── descriptor.v1
  │     ├── Pinecone namespace: org_17_voyager
  │     ├── Connector: webhook (push from Fluent Bit)
  │     └── Conversations: [...]
  └── Project: Payments Service
        ├── descriptor.v1
        ├── Pinecone namespace: org_17_payments
        ├── Connector: CloudWatch
        └── Conversations: [...]
```

**What is per-project:** descriptor, Pinecone namespace, connector config, MCP endpoint.  
**What is shared:** agent loop, tool implementations, ingestion pipeline, prompt templates, eval harness, API, UI.

### The descriptor (replacing per-app code)

A confirmed YAML file, auto-generated by the Profiler Agent from sample logs:

```yaml
domain_id: cms3
display_name: CMS3 Journey Engine
correlation_keys:
  primary: execution_id
  secondary: customer_id
group_by: [customer_id, execution_id]
identifiers:
  actor: customer_id
  flow: journey_id
  unit: step_order
  location: page_path
timestamp_field: timestamp
level_field: level
message_field: message
error_signals:
  fields: [error_code, error_message]
  level_values: [error, critical]
vocabulary:
  event_unit: step
  flow_unit: journey
  actor_unit: customer
  routing_unit: route
known_patterns:
  - "GraphQL has two representations: transport-level graphql_request events and named gql_* operations. These are NOT duplicates."
  - "route_entered events define the navigation path of a journey."
domain_description: >
  CMS3 is a CMS agent journey orchestration engine. It routes agents through multi-step journeys, evaluates UI conditions at each step, and fires GraphQL API calls. Failures can be routing misconfigurations, condition evaluation errors, or API failures.
```

This descriptor is injected into every prompt, every scope extractor call, and every tool invocation. No CMS3-specific Python code required.

### v2 architecture (target)

```
User question
        ↓
POST /api/v2/projects/{project_id}/chat
        ↓
Load project descriptor
        ↓
Tool-calling Agent Loop (LangGraph ReAct):
  System prompt + descriptor injected
  Agent decides which tools to call, in what order:

  Tools available:
    search_logs(query, filters)           → vector search + rerank in project namespace
    get_event_group(correlation_id)       → fetch one logical run by primary key
    get_timeline(filters)                 → chronological event sequence
    get_code_context(symbol_or_file)      → via MCP / repo index
    get_recent_changes(file, since)       → via MCP / git blame
    classify_issue(evidence)              → bug | business_condition | unknown
    clarify_with_user(question)           → ask for missing scope
    create_jira_ticket(structured_report) → only when manager explicitly requests
        ↓
Answer grounded in logs + code (SSE streaming)

Notes on v2 architecture:
- Descriptor is injected into the system prompt at conversation start — NOT fetched as a runtime tool.
- Reranking (FlashRank) moves inside `search_logs` — it runs on every vector search, not as a separate graph node.
- Multi-turn memory: per-project thread IDs via MemorySaver (same as v1); switching projects within a session resets the thread.
- classify_issue guarantee: unlike v1 where it is a mandatory final node, in v2 it is a tool the agent MAY skip. A post-processing guard must ensure every completed investigation is classified before the response is returned — agent cannot bypass it.
```

### Ingestion pipeline (descriptor-driven, source-agnostic)

```
Connector (S3 | CloudWatch | webhook | file upload | ...)
        ↓
RawLogEvent envelope (source-agnostic)
        ↓
PII scanner
        ↓
Descriptor-driven normaliser
  (reads descriptor.correlation_keys, .identifiers, .group_by, etc.)
        ↓
Chunker: event chunks + group summary chunks
        ↓
Embedder → Pinecone (project namespace)
```

The normaliser and chunker have no CMS3-specific code. They are driven entirely by the descriptor.

---

## 6. Architecture Overview

### Layer diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT SOURCES (per project, user configured)                   │
│  File Upload │ S3 │ CloudWatch │ Datadog │ Webhook │ Kafka ...  │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│  CONNECTOR LAYER                                                 │
│  • Auth + secret vault                                          │
│  • Pull / push / stream                                         │
│  • Incremental checkpoint + deduplication                       │
│  • Rate limiting, backoff, health monitoring                    │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓ RawLogEvent
┌─────────────────────────────────────────────────────────────────┐
│  INGESTION PIPELINE                                              │
│  PII scan → descriptor-driven normalise → chunk → embed → store │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓ Pinecone namespace (per project)
┌─────────────────────────────────────────────────────────────────┐
│  AGENT RUNTIME (identical for all projects)                     │
│  Tool-calling agent loop + descriptor-aware system prompt       │
│  Tools: search_logs, get_group, timeline, code_context, jira    │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│  API + UI                                                        │
│  FastAPI SSE  │  Project management UI  │  Onboarding form      │
└─────────────────────────────────────────────────────────────────┘
```

### Onboarding flow (new project)

```
Create project
        ↓
Choose connector → configure credentials → test connection
        ↓
Pull sample (200–1000 events)
        ↓
Profiler Agent analyses sample:
  • auto-detect correlation keys, identifiers, error signals
  • infer vocabulary from field names and values
  • detect known patterns (e.g. GraphQL duality)
  • confidence score per field
        ↓
Descriptor form rendered (user sees):
  • 7 primary fields (pre-filled, editable)
  • Confidence indicators per field
  • Live preview: "here is how one execution group looks"
  • Paste 5 example questions you'd ask
        ↓
User confirms (or edits + confirms)
        ↓
Full ingestion job triggered → project live
```

### MCP codebase integration

Each project can optionally connect a code repository. This unlocks:

- `get_code_context(symbol)` → find the function that emits a log line
- `get_recent_changes(file)` → correlate errors with recent commits
- Grounding answers in both logs _and_ code — not log text alone

Implementation options (in priority order):

1. **MCP server the user already runs** — MoveMind connects as a client
2. **MoveMind-hosted repo index** — user grants a read-only OAuth token; MoveMind indexes the repo with code embeddings
3. **Local MCP server packaged with MoveMind** — for self-hosted or enterprise deployments

---

## 7. Phased Delivery Plan

### Phase 0 — Foundation cleanup (3–4 weeks)

Goal: make v1 production-stable and document all CMS3 coupling points before any generics work begins.

| Task | Why | Effort |
| --- | --- | --- |
| Complete v1 system audit (see `docs/tracking/system-audit.md`) | Know exactly what exists before changing it | 1–2 days |
| Latency optimisations (see system-audit Layer 5) | Must be < 10s before any new users | 1 week |
| Jira ticket creation (P-05): Jira API client + manager-triggered flow | Complete the CMS3 product first | 1 week |
| Deep technical report + steps-to-reproduce generator (P-06, P-07) | Inside the Jira ticket | 1 week |
| Add `domain_id` field to `GraphState` | Route future multi-app logic by project | 1 day |

> **Note on Jira scope:** P-05 to P-07 together (Jira client, technical report generator, steps-to-reproduce, manager-triggered conversation flow) is a full 2-week track of its own. Phase 0 should not be treated as a single 2-week sprint — it is 3–4 weeks total. Do not start Phase 1 generics work until CMS3 v1 is demonstrably feature-complete.

Milestone: **MoveMind v1 for CMS3 is feature-complete and production-ready.**

---

### Phase 1 — Descriptor + descriptor-driven ingestion (6–8 weeks)

Goal: decouple ingestion and prompts from CMS3. CMS3 continues to work, now driven by a descriptor.

| Task | Detail |
| --- | --- |
| Define `Descriptor` schema (Pydantic model + YAML serialisation) | The central contract for all future work |
| Refactor `preprocessing.py` → descriptor-driven normaliser | Replace hardcoded CMS3 fields with descriptor lookups |
| Refactor `retrieval.py` → remove `build_api_timeline_documents()` CMS3 logic | Replace with descriptor-driven timeline tool; remove `CID_PATTERN` / `PAGE_PATTERN` hardcoded regexes |
| Fix `_processed_chunk_docs()` `lru_cache` singleton | Cache must be keyed by project namespace, not a global singleton — multi-project **will break** without this |
| Refactor `config.py` → replace `PINECONE_NAMESPACE`, `RAW_LOGS_PATH`, `PROCESSED_CHUNKS_PATH` singletons | These must become per-project runtime values, not global settings |
| Parameterise all 4 affected prompts in `templates.py` | `_REWRITE_PROMPT`, `_MANAGER_ANSWER_PROMPT`, `_DEVELOPER_ANSWER_PROMPT`, `CMS3_CONTEXT_SCHEMA` — replace CMS3 hardcoding with `{domain_description}`, `{vocabulary}`, `{chunk_schema}` variables |
| Refactor `resolve_context.py` → descriptor-driven scope extraction | Regex extractors become configurable via descriptor |
| Refactor `generate_answer.py` → remove `CMS3_CONTEXT_SCHEMA` import | Inject descriptor vocabulary into prompts instead |
| Refactor `GraphState` → replace CMS3 fields with `scope: dict[str, Any]` | Eliminate per-domain state fields |
| Remove / replace `ingestion.py:verify_vectorstore()` hardcoded CMS3 query | Replace with a descriptor-driven sanity check |
| CMS3 descriptor file (`data/descriptors/cms3.yaml`) | CMS3 re-expressed as a descriptor; proves the approach |
| Ingestion reads descriptor from project config | Normaliser driven by the file, not hardcoded fields |
| Add Pinecone namespace isolation per project | Foundation for multi-tenancy |

Milestone: **CMS3 works identically, now driven by its descriptor. Zero CMS3-specific Python code remains outside the descriptor file.**

---

### Phase 2 — Tool-calling agent + second project (6–8 weeks)

Goal: prove the architecture on a second real application.

| Task | Detail |
| --- | --- |
| Replace fixed LangGraph graph with ReAct tool-calling agent | Agent decides tool order; descriptor in system prompt |
| Implement core tools: `search_logs`, `get_event_group`, `get_timeline` | Each reads from project namespace + uses descriptor |
| Implement `classify_issue` tool (replaces current node) | Same logic, now a callable tool |
| Implement `clarify_with_user` tool | Agent asks for missing scope gracefully |
| Profiler Agent (batch mode — no UI yet) | Given 200 events, emit a candidate descriptor |
| Onboard Voyager (or second real app) using Profiler + descriptor | Real test of generic architecture |
| Eval: compare v2 agent answers against v1 for CMS3 | Quality must not regress |

Milestone: **Two applications live on the same agent. Profiler can generate a working descriptor from sample logs without code changes.**

---

### Phase 3 — SaaS shell (6–8 weeks)

Goal: turn the engine into a product.

| Task | Detail |
| --- | --- |
| Organisation + Project data model (PostgreSQL) | Multi-tenant foundation |
| Auth (JWT, OAuth, team invites) | Self-serve sign-up |
| Project management UI | Create project, view status, view conversations |
| Onboarding UI (descriptor form + live preview) | The user-facing profiler experience |
| Webhook connector (push endpoint) | Self-serve "connect anything" escape hatch |
| S3 connector (batch pull, event-triggered) | First real connector |
| Incremental ingestion checkpoint + deduplication (ships with S3 connector) | S3 connector without checkpointing re-ingests everything every run — these are inseparable |
| PII scanner before ingestion | Required before any real customer data passes through the pipeline; cannot be deferred past Phase 3 |
| Connector health monitoring + user-visible status | "Last sync: 3h ago ⚠️" |
| Per-project billing meters (events ingested, questions asked, tokens) | Foundation for monetisation |

Milestone: **A new user can sign up, create a project, upload logs, and start asking questions — without talking to anyone at MoveMind.**

---

### Phase 4 — Connectors + code context (demand-driven, 6–10 weeks)

Goal: connect to where logs actually live and ground answers in code.

| Task | Detail |
| --- | --- |
| CloudWatch connector | Most common for AWS customers |
| Datadog / Elastic / Splunk connector | Driven by which design partners need it |
| MCP client integration (code context tool) | Read-only repo connection per project |
| MoveMind-hosted repo indexer (fallback for no MCP server) | OAuth token → code embeddings → `get_code_context` tool |
| Kafka / Kinesis streaming (optional) | Only if real-time demand confirmed by customers |

Milestone: **Design partners have their logs syncing automatically. The agent can reference code when answering. Zero manual ingestion steps.**

---

## 8. Key Challenges

### C-01 — Log schema diversity (hardest technical problem)

Logs across applications vary wildly:

- **Structured JSON** (like CMS3) — best case
- **Unstructured text** (nginx, Python tracebacks, syslog) — require parsing
- **OpenTelemetry / distributed traces** — structured but different mental model (spans, parent IDs, services)
- **Mixed streams** — JSON lines interleaved with stack traces from multiple services

**The profiler will fail for some log shapes.** Manual mode escape hatch is non-optional. Every descriptor field needs an override mechanism.

**Risk:** Medium-high. Mitigated by starting with well-structured JSON logs (S3 exports, CloudWatch structured logging) before tackling raw text.

---

### C-02 — Profiler accuracy

Given 200 sample events, the Profiler Agent must reliably infer:

- Correct correlation keys
- Correct grouping strategy
- Domain vocabulary

LLMs are surprisingly good at this — but will make wrong guesses on ambiguous schemas, low-cardinality fields, or sparse samples. A wrong descriptor produces silent quality degradation, not a crash.

**Mitigation:** Confidence scores per field. Live preview of one execution group. Clear "fix this" affordances in the descriptor form. Design for user correction, not profiler perfection.

**Risk:** Medium. Manageable with good UX; dangerous if the form is trusted blindly.

---

### C-03 — Quality gap between generic + hand-tuned

MoveMind v1 is hand-tuned for CMS3. The generic agent will be measurably worse at CMS3 questions initially. This is an expectation management and engineering problem.

**Mitigation:** Maintain the v1 CMS3 eval dataset (`app/eval/`). Run it against v2 before releasing. Accept a short-term quality dip with a committed timeline to close the gap.

**Risk:** Medium. The gap is closeable. The risk is users seeing a degraded experience before it's closed.

---

### C-04 — Credentials and secrets management

Once connectors exist, MoveMind holds AWS IAM credentials, Datadog API tokens, GitHub OAuth tokens, and Splunk credentials for every customer. This is a significant security surface.

**Requirements (non-negotiable before enterprise customers):**

- Secret vault (AWS Secrets Manager or equivalent)
- Key rotation and revocation
- Audit logs for all credential access
- Cross-account IAM role assumption (not API keys) for AWS
- Read-only scoping enforced everywhere

**Risk:** High if under-engineered. This is 2–3 weeks of focused work done properly. Do not defer it once connectors are live.

---

### C-05 — Scale and cost at volume

A real production log stream is 10M–1B events/day. At OpenAI embedding prices, 100M events per day per customer is economically unsustainable without mitigation.

**Mitigations:**

- Sampling: embed 1-in-N events for high-volume streams
- Tiered retention: last 24h fully indexed; older logs in object storage (query only on demand)
- Aggregation: group low-signal events before embedding
- Customer-set filters: users define what log levels / services to ingest

Pricing model must reflect events ingested per day, not conversations. Define this before Phase 3.

**Risk:** High if not designed upfront. The wrong pricing model makes enterprise customers economically destructive.

---

### C-06 — Log-to-code correlation

Matching a log line to its source code is non-trivial:

- Log messages are interpolated strings — exact grep fails
- Messages come from libraries you don't own
- Symbol names change over time with refactoring
- Large monorepos exceed any practical context window

**Approach:** tiered matching:

1. Exact substring search in repo
2. Semantic embedding search over code chunks
3. LLM reasoning over top candidates

No approach is perfect. The code context tool must be honest about uncertainty in its output.

**Risk:** Medium. Real value is delivered even at 60% recall. Users understand it's approximate.

---

### C-07 — Descriptor drift

Applications change. Log schemas evolve silently. A descriptor confirmed 3 months ago may be subtly wrong today. The agent answers degrade with no obvious signal.

**Mitigations:**

- Schema drift detector: periodically compare fresh sample against current descriptor
- Alert user when new unknown fields appear in > 10% of recent events
- Descriptor versioning with ingestion pinned to a specific version
- "Re-profile" button in the UI

**Risk:** Medium-low for v1, grows with time. Build the drift detector before GA.

---

### C-09 — Pinecone storage cost at multi-project scale

C-05 covers OpenAI embedding/inference cost. Pinecone's per-vector storage cost is a separate and growing line item:

- 10 projects × 500K events × 1536 dimensions = ~7.5M vectors minimum
- Pinecone Serverless charges per read unit + per write unit + storage; this scales directly with project count and event volume
- A single high-volume customer (10M events/day) can consume Pinecone budget faster than they consume OpenAI budget

**Mitigations:** Same as C-05 — tiered retention, sampling, aggregation. Additionally: evaluate Pinecone Serverless vs. Pod-based pricing at different volume tiers before GA pricing is set.

**Risk:** Medium. Manageable, but must be modelled before pricing decisions are made.

---

### C-10 — `classify_issue` guarantee in the tool-calling agent

In v1, `classify_issue` is the mandatory final node — every investigation is always classified. In v2 with a ReAct agent, it becomes a callable tool the agent may choose not to invoke.

**Risk:** The product guarantee (manager always sees a bug/business-condition verdict) silently breaks if the agent short-circuits before calling `classify_issue`.

**Mitigation:** Post-processing guard in the agent loop — after the agent signals it is done, check whether `issue_type` is set in state. If not, force-call `classify_issue` before returning the response. This is a framework-level enforcement, not an agent instruction.

**Risk:** Low engineering complexity, high product impact if missed.

---

### C-08 — Agent loop reliability vs. fixed graph

Replacing the fixed LangGraph graph with a ReAct tool-calling agent gives flexibility — but introduces new failure modes:

- Agent picks wrong tools or wrong order
- Infinite loop if `clarify_with_user` is called repeatedly
- Non-deterministic behaviour makes debugging harder
- Harder to write deterministic evals

**Mitigations:**

- Max tool call depth (circuit breaker)
- Structured tool output contracts (Pydantic schemas for every tool return)
- Eval cases that assert tool call sequences, not just answer quality
- Keep the fixed graph as a fallback for high-confidence question patterns (pure retrieval)

**Risk:** Medium. Well-understood problem in the LangGraph ecosystem. Manageable with good tool contracts and evals.

---

## 9. Success Metrics

### Onboarding quality

- Profiler generates a working descriptor for ≥ 80% of well-structured JSON log samples on first attempt
- User confirms or makes ≤ 3 edits to primary fields before the descriptor is accepted (editing `domain_description` or `known_patterns` free-text does not count as a structural edit)
- Time from log upload to first question answered: < 5 minutes
- Ingestion of a 10K event log file completes in < 3 minutes (blocking the onboarding UX past this is unacceptable)

### Answer quality

- MoveMind v2 CMS3 eval score ≥ 95% of MoveMind v1 score (no regression)
- New project (second app) achieves Ragas faithfulness ≥ 0.75 and answer relevance ≥ 0.70 within 48h of descriptor confirmation — this is the concrete definition of "satisfactory"
- Faithfulness (Ragas): ≥ 0.85 across all projects at GA
- `classify_issue` is populated on 100% of completed investigations (not skipped by the agent)

### Reliability

- Connector sync success rate: ≥ 99%
- P95 answer latency: < 10s for tool-calling agent (same target as v1)
- Schema drift alert fires within 1 sync cycle of a log field change
- API uptime: ≥ 99.5% monthly (minimum SaaS bar)

### Business

- A new engineering team can onboard a project without MoveMind engineering involvement
- 3 design partners live on v2 SaaS before public launch
- Per-project cost (embedding + inference + storage) is understood and profitable at design-partner pricing

---

## 10. Out of Scope

The following are explicitly excluded from this SOW. They may be addressed in a future SOW.

| Item | Reason for exclusion |
| --- | --- |
| Mobile / native app | Web-first |
| Real-time streaming (Kafka/Kinesis) ingestion | Phase 4, demand-driven only |
| FullStory / LogRocket / session replay connectors | Different product line; separate descriptor model |
| On-premise / self-hosted deployment | Post-SOC2; enterprise track only |
| SOC 2 certification | Separate 6-month track |
| Automatic Jira ticket creation without manager approval | Deliberate product decision — manager must trigger |
| Public API / SDK for external developers | Post-GA |
| Training or fine-tuning custom models | Not planned; prompt + descriptor approach is sufficient |
| Support for non-JSON log formats (syslog, nginx text) | Phase 4+, after structured JSON use cases are proven |

---

## 11. Open Decisions

Items that must be decided before or during Phase 2.

| Decision | Options | Owner | Target |
| --- | --- | --- | --- |
| **Descriptor storage format** | YAML file in S3 / row in PostgreSQL / both | Engineering | Phase 1 |
| **Pinecone namespace strategy** | Per project vs. per project-version | Engineering | Phase 1 |
| **Agent framework** | Stay on LangGraph ReAct / move to OpenAI Assistants API / custom | Engineering | Phase 2 |
| **MCP strategy** | Self-hosted MCP server / MoveMind-hosted indexer / both | Engineering + Product | Phase 4 |
| **Pricing model** | Per event ingested / per question / per seat / hybrid | Product + Finance | Phase 3 |
| **Billing vendor** | Stripe / Lago / custom usage-based billing | Product + Engineering | Phase 3 |
| **Frontend stack** | React + TailwindCSS / Next.js / other | Engineering | Phase 3 |
| **PII redaction** | Client-side only / server-side scanner / user opt-in | Legal + Engineering | Phase 3 (before GA) |
| **Secret management vendor** | AWS Secrets Manager / HashiCorp Vault / Doppler | Engineering | Phase 3 |
| **Database migration strategy** | How CMS3 v1 data (flat Pinecone namespace) migrates to multi-tenant project schema without data loss | Engineering | Phase 1 → Phase 3 |
| **Conversation retention policy** | How long conversations are stored; user-deletable? GDPR implications | Legal + Product | Phase 3 |
| **Second design-partner application** | Voyager / Payments / external customer | Product | Phase 2 |

---

_This document is a living artefact. Update decisions, add new challenges, and revise timelines as work progresses. The next document to produce from this is `docs/architecture/v2-architecture.md` — the detailed technical architecture for Phases 1 and 2._
