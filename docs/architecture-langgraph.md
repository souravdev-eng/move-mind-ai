# LangGraph Architecture

> Last updated: 2026-04-10
> Branch: feat/eval

---

## Current Architecture (as built today)

```
Manager types a question
          │
          ▼
┌─────────────────────┐
│   classify_question │  Model: gpt-4o-mini
│                     │  Is this a new question or a follow-up?
└─────────────────────┘
          │
    ┌─────┴──────┐
    │            │
"retrieve"   "rewrite"
    │            │
    │   ┌────────────────────┐
    │   │  rewrite_question  │  Model: gpt-4o-mini
    │   │                    │  Rewrites follow-up into a
    │   │                    │  self-contained question
    │   └────────────────────┘
    │            │
    └─────┬──────┘
          │
          ▼
┌─────────────────────┐
│   resolve_context   │  No LLM — pure logic
│                     │  Extracts from question text:
│                     │  → CID / customer_id
│                     │  → execution_id
│                     │  → page_path / route
│                     │  → analysis_mode (api_calls | general)
│                     │  → api_view (named | transport | all)
│                     │  Persists these across turns in state
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   retrieve_docs     │  Pinecone vector search
│                     │  Hybrid: summaries (k=2) + events (k=8)
│                     │  Scoped by: CID, page_path, chunk_type
│                     │  Special case: API timeline queries →
│                     │  build_api_timeline_documents() instead
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   rerank_docs       │  FlashRank (ms-marco-TinyBERT)
│                     │  Reranks retrieved chunks → top 5
│                     │  Skipped if API timeline (already structured)
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   generate_answer   │  Model: gpt-4o (smart)
│                     │        or o3 (thinking) for "why/root cause"
│                     │  Generates answer from reranked context
│                     │  Special case: API count conflict →
│                     │  asks clarification instead
└─────────────────────┘
          │
          ▼
       [END]
    Answer returned to manager
    (technical, not plain English — current gap)
```

---

## State — What Flows Between Nodes

```
GraphState
├── messages              ← Full chat history (HumanMessage + AIMessage)
├── original_question     ← What the manager actually typed
├── question              ← Current question (may be rewritten)
├── query_type            ← "retrieve" | "rewrite"
│
├── active_customer_id    ← CID — persists across turns ✓
├── active_execution_id   ← Execution ID — persists across turns ✓
├── active_page_path      ← Route/page — persists across turns ✓
├── analysis_mode         ← "api_calls" | "general"
├── api_view              ← "named_operations" | "transport_requests" | "all_api_types"
├── requested_api_count   ← Numeric count if mentioned ("all 9 APIs")
│
├── documents             ← Raw retrieved chunks from Pinecone
├── reranked_documents    ← After FlashRank (top 5)
└── answer                ← Final text answer
```

---

## What Each Node Uses

| Node | Input from State | Output to State | Model / Tool |
|------|-----------------|-----------------|-------------|
| `classify_question` | `question`, `messages` | `query_type` | gpt-4o-mini |
| `rewrite_question` | `question`, `messages` | `question` | gpt-4o-mini |
| `resolve_context` | `question`, `messages`, all `active_*` | `active_customer_id`, `active_execution_id`, `active_page_path`, `analysis_mode`, `api_view`, `requested_api_count` | No LLM |
| `retrieve_docs` | `question`, `active_customer_id`, `active_page_path`, `analysis_mode` | `documents` | Pinecone |
| `rerank_docs` | `documents`, `question` | `reranked_documents` | FlashRank |
| `generate_answer` | `reranked_documents`, `question`, `original_question`, all `active_*`, `messages` | `answer`, `messages` | gpt-4o / o3 |

---

## Target Architecture — End of Week 1

Adding `classify_issue` after `generate_answer`.

```
Manager types a question
          │
          ▼
    classify_question
          │
    ┌─────┴──────┐
    │            │
"retrieve"   "rewrite"
    │            │
    │   rewrite_question
    │            │
    └─────┬──────┘
          │
    resolve_context
          │
    retrieve_docs
          │
    rerank_docs
          │
    generate_answer  ← Now uses manager-tuned plain English prompt
          │
          ▼
┌─────────────────────┐        ◄── NEW (Day 5)
│   classify_issue    │  Model: gpt-4o
│                     │  Reads the answer + retrieved evidence
│                     │  Classifies:
│                     │  → "bug" (system behaved incorrectly)
│                     │  → "business_condition" (intentional config)
│                     │  → "unknown" (not enough evidence)
│                     │  Outputs: issue_type + confidence score
└─────────────────────┘
          │
          ▼
       [END]
    Response to manager:
    ┌─────────────────────────────────┐
    │ Plain English explanation       │
    │ ─────────────────────────────── │
    │ Classification: BUG             │
    │ Confidence: 87%                 │
    └─────────────────────────────────┘
```

**New state fields (Week 1):**
```
├── explanation_mode   ← "manager" | "developer"   (Day 2)
├── issue_type         ← "bug" | "business_condition" | "unknown"  (Day 5)
└── issue_confidence   ← 0.0 – 1.0   (Day 5)
```

---

## Target Architecture — End of Week 2

Adding Jira ticket creation as a tool, triggered by manager instruction.

```
Turn 1 (Investigate):
  Manager: "What happened to CID 7093495?"
  → Full pipeline runs → Plain English answer + classification

Turn 2 (Manager decides):
  Manager: "This looks like a bug. Create a Jira ticket."
  → classify_question detects ticket creation intent
          │
          ▼
┌──────────────────────────┐        ◄── NEW (Week 2)
│   build_technical_report │  Model: o3
│                          │  Goes deep into retrieved evidence
│                          │  Builds:
│                          │  → Root cause (technical)
│                          │  → Affected journey steps
│                          │  → Steps to reproduce
│                          │  → Log evidence (CID, execution, env)
│                          │  → Suggested fix approach
└──────────────────────────┘
          │
          ▼
┌──────────────────────────┐        ◄── NEW (Week 2)
│   create_jira_ticket     │  Tool: Jira API
│                          │  Formats structured content into ticket
│                          │  Creates ticket via Jira REST API
│                          │  Returns: ticket URL + ticket ID
└──────────────────────────┘
          │
          ▼
       [END]
    Manager sees: "Ticket created → PROJ-1234"
    Developer sees: fully structured Jira ticket
```

**New state fields (Week 2):**
```
├── ticket_intent      ← bool — did manager ask to create a ticket?
├── technical_report   ← structured dict — root cause, steps, evidence
└── jira_ticket_url    ← str — link to created ticket
```

---

## Notes

- **MemorySaver** checkpointer persists `GraphState` across turns using `thread_id` (session_id from API)
- **Conditional routing** only exists at `classify_question` today — future may add routing at `classify_issue` for ticket vs. no-ticket paths
- **o3 (thinking model)** is triggered by keywords: "why", "root cause", "failure", "explain" — will be the default for `build_technical_report`
