# Move Mind AI — System Audit

> Last updated: 2026-04-10
> Branch: feat/eval
> Purpose: Track the gap between what the product needs and what exists today. Update status as work progresses.

---

## Legend

| Status | Meaning |
|--------|---------|
| 🔴 Missing | Not built at all |
| 🟠 Partial | Started but incomplete or wrong scope |
| 🟡 In Progress | Being worked on now |
| 🟢 Done | Complete and verified |
| ⚪ Deferred | Known, accepted for later |

---

## The Correct Product Flow

```
CMS Agent hits an issue during their journey
        ↓
Agent reports to their Manager
        ↓
Manager opens Move Mind AI (manager-facing app)
Manager asks: "Why did this happen?" + provides CID / logs
        ↓
AI investigates the logs and journey
        ↓
AI responds in PLAIN ENGLISH
(Manager understands without any technical knowledge)
        ↓
Manager decides:
    "This looks like a real bug"      OR     "This is a system config condition"
        ↓                                            ↓
Manager instructs AI:                     Manager instructs AI:
"Create a developer ticket for this bug"  "Create a ticket to update the config"
        ↓
AI goes DEEP — gathers full technical context:
  - Root cause (technical)
  - Affected journey steps
  - Relevant log evidence
  - Steps to reproduce the bug (for developer)
  - CID, execution ID, environment, release
        ↓
AI creates Jira ticket with all structured content
        ↓
Developer receives a fully formed ticket
Developer reproduces → fixes → done
(Developer was never involved in the investigation)
```

**Key principles from this flow:**
1. **Manager is the primary user** — not the agent, not the developer
2. **Plain English first, always** — investigation output is never technical
3. **Jira creation is a deliberate second step** — manager triggers it by instruction, not automatic
4. **Developer only sees the final ticket** — never pulled into investigation
5. **Steps to reproduce are mandatory** in every ticket — developer must be able to reproduce without asking anyone
6. **The conversation is sequential** — Turn 1: explain. Turn 2: manager decides. Turn 3: create ticket.

---

## What Exists Today (The Actual System)

The current system is a **RAG-based log debugging chatbot**. It covers one part of the flow well — investigating logs and answering questions — but the surrounding product structure is missing.

```
User types a question (free text)
        ↓
POST /api/v1/chat
        ↓
LangGraph RAG workflow:
  classify_question   → retrieve or rewrite? (query type only)
  rewrite_question    → fix follow-up questions using history
  resolve_context     → extract CID, page_path, execution_id from text
  retrieve_docs       → Pinecone hybrid search (summaries k=2 + events k=8)
  rerank_docs         → FlashRank top-5
  generate_answer     → gpt-4o / o3 with retrieved context
        ↓
Answer + sources (streaming SSE)
```

---

## Product Capability Gap Map

| # | Capability | Status | Current Reality |
|---|-----------|--------|----------------|
| P-01 | Plain English explanation of the issue (for manager) | 🟢 Done | MANAGER_ANSWER_PROMPT added with strict no-jargon rules and What happened / Why / What this means format |
| P-02 | Structured issue intake (CID + logs submitted by manager) | 🔴 Missing | Only a free-text chat input. No CID field, no log upload, no structured submission |
| P-03 | Real-time log ingestion at submission time | 🔴 Missing | Batch-only. All logs pre-indexed offline via scripts. No live ingest API |
| P-04 | Issue classification: real bug vs. business/config condition | 🔴 Missing | `classify_question.py` classifies query type (retrieve/rewrite), not issue type |
| P-05 | Manager-triggered Jira ticket creation ("create a ticket") | 🔴 Missing | Zero Jira integration. No tool, no client, no config |
| P-06 | Deep technical report generation (for inside the Jira ticket) | 🟠 Partial | o3 reasoning mode exists but produces a chat answer, not a structured developer report |
| P-07 | Steps to reproduce in the ticket | 🔴 Missing | No prompt or node generates reproduction steps |
| P-08 | Issue deduplication — has this happened before? | 🔴 Missing | No issue history, no fingerprinting, no similarity tracking across reports |
| P-09 | Recurring issue flagging — mark as high priority | 🔴 Missing | No frequency tracking, no priority scoring |
| P-10 | Issue persistence — store reports, status, ticket links | 🔴 Missing | Fully ephemeral. No database, no issue schema |

---

## What Works Well (Foundation to Build On)

| Component | File | Strength |
|-----------|------|---------|
| CID / execution_id / page_path extraction | `app/graphs/nodes/resolve_context.py` | Persists across multi-turn conversation |
| Hybrid retrieval (summaries + events) | `app/rag/retrieval.py` | Good context coverage per CID |
| FlashRank reranking | `app/chains/reranker_chain.py` | Reduces noise in retrieved context |
| Multi-turn session memory | `app/graphs/state.py` + MemorySaver | Carries active CID/context across turns — critical for the 3-turn flow |
| API timeline special-case handling | `app/rag/retrieval.py:build_api_timeline_documents()` | Structured journey view |
| SSE streaming | `app/api/routes/chat.py` | Real-time token delivery |
| Multi-model routing | `app/utils/helpers.py` | fast / smart / thinking presets |
| Log preprocessing + chunking | `app/rag/preprocessing.py` | Execution summaries + event chunks |

---

## Technical Gaps (Inside Existing Components)

Issues within the parts that already exist.

| ID | File | Issue | Status |
|----|------|-------|--------|
| T-01 | `tests/test_chains.py` | Imports `app.chains.base.build_simple_chain` — module does not exist | 🟢 Done |
| T-02 | `tests/test_graphs.py` | Imports `build_agent_graph` — actual function is `build_rag_graph()` | 🟢 Done |
| T-03 | `tests/test_rag.py` | Imports `split_documents`, `load_documents` — neither exists in `app.rag.ingestion` | 🟢 Done |
| T-04 | `scripts/ingest.py` | Calls `ingest()` which does not exist. Should call `build_vectorstore()` | 🟢 Done |
| T-05 | `app/config.py` | LangSmith tracing configured but not wired into graph runs | 🟠 Partial |
| T-06 | `app/tools/search.py` | `web_search()` always returns stub — never integrated | ⚪ Deferred |
| T-07 | `app/` | No evaluation harness. README describes Ragas but no code implements it | 🔴 Missing |
| T-08 | — | No golden eval dataset — cannot measure reliability | 🔴 Missing |

---

## What Needs to Be Built (Prioritized)

### Layer 1 — Make the Current RAG Core Reliable
*The investigation quality is the foundation of everything. If the plain English explanation is wrong, nothing else matters.*

| What | Why |
|------|-----|
| Tune `ANSWER_PROMPT` for manager audience (plain English, no jargon) | P-01 — First thing the manager sees |
| Fix broken tests (T-01 through T-04) | Safety net before any changes |
| Golden eval dataset — 30 Q&A pairs by category | Can't improve what can't be measured |
| Ragas eval pipeline (faithfulness, relevancy, precision, recall) | Repeatable metrics on every change |

### Layer 2 — Issue Classification + Conversation Flow
*Manager needs to understand what type of issue it is before deciding to create a ticket.*

| What | Why |
|------|-----|
| Issue classifier node — real bug vs. business/config condition | P-04 — Core product value |
| Classification shown clearly in the manager response | Manager must know what they're deciding on |
| Multi-turn flow: explain → manager decides → create ticket | The 3-step conversation |

### Layer 3 — Jira Ticket Creation
*The output that makes the developer's job easy.*

| What | Why |
|------|-----|
| Jira tool (jira-python client + API config) | P-05 — End-to-end requirement |
| Deep technical report generator (structured developer content) | P-06 — What goes inside the ticket |
| Steps to reproduce generator | P-07 — Mandatory for developer usefulness |
| Manager-triggered ticket creation via conversation instruction | P-05 — Manager says "create ticket", AI does it |

### Layer 4 — Issue Lifecycle & Dedup
*Long-term value — prevent repeat mistakes.*

| What | Why |
|------|-----|
| Issue persistence (DB + schema) | P-10 — Store reports, status, ticket links |
| Issue fingerprinting + deduplication | P-08 — "We've seen this before" |
| Recurring issue flagging + priority scoring | P-09 — Don't keep fixing the same thing |

---

## Decisions & Notes

> Add design decisions, pivots, and important context here as work progresses.

- **2026-04-10**: Initial audit — system is a working RAG chatbot but the issue lifecycle layer is fully missing.
- **2026-04-10**: Corrected product flow. Manager is the primary user. Flow is: investigate (plain English) → manager decides → create Jira ticket. Developer is never in the investigation loop. Steps to reproduce are mandatory in every ticket.
