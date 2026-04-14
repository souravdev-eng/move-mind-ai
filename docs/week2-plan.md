# Week 2 Plan — Observability & Eval Hardening

> Sprint: 2026-04-14 to 2026-04-21
> Branch: feat/eval (continues) → feat/observability
> Goal: Make every run measurable, traceable, and regression-safe. Before we add agentic loops (CRAG, self-reflection) in Week 3, we must be able to *see* what the graph is doing on every real and synthetic request.

---

## Why This Week (The "Why" Before The "How")

Week 1 gave us a **point-in-time** measurement — a baseline from 27 golden Q&As. That is not the same as **continuous** measurement. Today we cannot answer:

1. What did the graph actually do on the last real user question?
2. How long did each node take, how many tokens did each LLM call consume, what did each cost?
3. Did last night's prompt tweak improve or regress faithfulness vs. the baseline?
4. Of 100 real production runs, how many had retrieval-miss? Hallucination? Wrong classification?

Without these answers we are flying blind. Any agentic loop we add next week will be impossible to tune safely.

---

## Legend

| Status | Meaning |
|--------|---------|
| 🔴 Not Started | Planned, not begun |
| 🟡 In Progress | Currently being worked on |
| 🟢 Done | Completed and verified |
| ⚪ Blocked | Waiting on dependency |

---

## Part A — What You Need To Learn (Concepts)

> Read / skim these before writing code. Each maps to one or more tasks in Part B.
> **For packages, docs links, YouTube search queries, and courses per concept, see `docs/week2-learning-resources.md`.**
> **For chapter-level reading from books you already own, see `docs/book-map.md`.**

### A.1 — Tracing vs Logging vs Metrics vs Evaluation

Four distinct things; confusing them is the #1 beginner mistake.

| Signal | Question it answers | Example in our graph |
|--------|--------------------|-----------------------|
| **Trace** | What happened, in what order, for *this one* request? | classify_question(120ms) → retrieve_docs(800ms, 8 chunks) → rerank_docs(300ms) → generate_answer(2.1s, 950 tokens) |
| **Log** | What interesting event happened inside a node? | "rerank_docs dropped 5 of 8 chunks below 0.3 score" |
| **Metric** | What is the aggregate behavior over N requests? | p95 latency = 6.3s; cost/query = $0.018; retrieval_miss_rate = 12% |
| **Eval** | Is the *quality* of output good, measured against ground truth or a judge? | faithfulness = 0.74 on golden set; online judge flags 1 in 20 answers as ungrounded |

**Key insight:** eval without tracing is blind debugging. When faithfulness drops from 0.80 → 0.65, the trace tells you *which node* caused it.

### A.2 — The Run Tree (Spans and Parent/Child)

LangGraph emits a tree: the graph invocation is the root span, each node is a child span, each LLM call is a grandchild span.

```
run: investigate_cid("CID-123")        [root, 4.2s]
├── node: classify_question            [110ms]
│   └── llm: gpt-4o-mini                [90ms, in=230 out=4 tok]
├── node: resolve_context               [50ms]
├── node: retrieve_docs                 [800ms]
│   └── tool: vectorstore.similarity    [780ms, k=8]
├── node: rerank_docs                   [310ms]
│   └── llm: cohere-rerank              [280ms]
├── node: generate_answer               [2.1s]
│   └── llm: gpt-4o                     [2.0s, in=3200 out=420 tok]
└── node: classify_issue                [820ms]
    └── llm: gpt-4o                     [790ms, in=900 out=60 tok]
```

Everything else (cost attribution, slow-node detection, regression blame) is built on this tree.

### A.3 — LangSmith (our chosen backend)

Why LangSmith over Langfuse / Arize / raw OTel for us: native LangGraph integration means **the run tree above is free** — no manual span creation. We only pay to add richer attributes (user_id, cid, issue_type) and to wire datasets + online evaluators.

Concepts to internalize:
- **Project** — a namespace for runs (one per environment: `move-mind-dev`, `move-mind-prod`)
- **Run** — one graph invocation, stored as a tree
- **Dataset** — golden examples; our Week 1 `golden_dataset.json` gets uploaded here
- **Evaluator** — a function (LLM-as-judge or code) run over a dataset or live runs
- **Tag / Metadata** — arbitrary key/values attached to runs for filtering (e.g., `env=prod`, `cid=123`)

### A.4 — Tokens, Cost, and Latency Attribution

A Senior AI engineer's muscle memory:
- Know the token price of every model you use (per 1M input / output tokens).
- Cost of a graph run = Σ (tokens_in × price_in + tokens_out × price_out) across all LLM spans.
- **Critical distinction:** model latency is not the same as node latency. `generate_answer` can be 2.1s with only 2.0s spent in the LLM — the other 100ms is prompt assembly + parsing. Track both.
- p50 tells you typical UX; p95 tells you tail UX; **p99 tells you when users rage-quit**.

### A.5 — Online Evaluators vs Offline Eval

- **Offline** (what we have): run the golden dataset on demand; compare to baseline.
- **Online**: sample a fraction of real production runs, send them to an LLM judge, grade faithfulness / relevancy continuously.

Online is what catches drift (e.g., an external API starts returning noisier chunks and our faithfulness quietly drops).

### A.6 — Regression Gates

An eval run that produces a number but does not **gate** anything is decoration. A regression gate is a rule like:

> "Fail the PR if faithfulness drops > 3% vs `data/eval/baseline_results.json`."

This is what separates a notebook-grade project from a production system.

### A.7 — Failure Modes of RAG (What We're Watching For)

| Failure mode | Signature in trace/metrics |
|--------------|----------------------------|
| Retrieval miss | `retrieve_docs` returns chunks but none semantically match the question (context_recall ≈ 0) |
| Hallucination | Answer contains entities or claims not present in retrieved chunks (faithfulness < 0.5) |
| Context overflow | Rerank keeps too many chunks; `generate_answer` prompt > model context |
| Classification miss | `classify_question` picks "retrieve" when "rewrite" was needed (eval on classification accuracy) |
| Silent model change | Provider deprecates / updates underlying model; latency + cost shift unexplained |

---

## Part B — What You Will Implement (Tasks)

### Definition of Done (Week 2)

- [ ] Every graph run produces a LangSmith trace with per-node spans, token counts, and cost
- [ ] `scripts/run_eval.sh` uploads results to LangSmith and writes a diff against `baseline_results.json`
- [ ] CI (or local pre-commit) blocks commits where faithfulness / relevancy drops > 3%
- [ ] Online judge grades 10% of real runs for faithfulness; results visible in LangSmith
- [ ] `docs/observability.md` documents: how to view a trace, how to read the dashboard, how to debug a bad answer using the trace
- [ ] `docs/system-audit.md` statuses updated

---

## Day 1 — Wire LangSmith Tracing

> Goal: see one real run as a tree.

| # | Task | Notes | Status |
|---|------|-------|--------|
| 1.1 | Create LangSmith account, project `move-mind-dev` | Free tier is enough | 🔴 Not Started |
| 1.2 | Add `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` to `.env.example` and loader | Do NOT commit the key | 🔴 Not Started |
| 1.3 | Verify tracing fires automatically from LangGraph — run one question, inspect the tree in UI | No code change should be needed beyond env vars | 🔴 Not Started |
| 1.4 | Add `@traceable` wrappers around any non-LangChain helper (e.g., custom retrievers in `app/rag/`) | Only where the auto-trace misses them | 🔴 Not Started |
| 1.5 | Confirm every node from `graph.png` appears as its own span | Screenshot for the docs | 🔴 Not Started |

**What you will learn:** auto-instrumentation vs manual; what a run tree actually looks like for your graph.

---

## Day 2 — Enrich Traces: Metadata, Cost, User Context

> Goal: a trace answers "what, for whom, how much, with which prompts".

| # | Task | Notes | Status |
|---|------|-------|--------|
| 2.1 | Attach metadata on every run: `cid`, `explanation_mode`, `env`, `issue_type` (added after classify) | Use `RunnableConfig.configurable` + `tags` | 🔴 Not Started |
| 2.2 | Ensure token counts are captured on every LLM call | LangChain chat models emit these; verify in UI | 🔴 Not Started |
| 2.3 | Add a cost-per-run computed field (input × price_in + output × price_out per model) | Keep a small `app/obs/pricing.py` table | 🔴 Not Started |
| 2.4 | Log structured events from nodes: `retrieve_docs` logs `k`, `num_returned`, `min_score`; `rerank_docs` logs `num_kept`, `cutoff` | These land on the corresponding span as attributes | 🔴 Not Started |
| 2.5 | Filter-test: in LangSmith UI, find "all runs where issue_type=bug AND faithfulness<0.7" | If the filter returns results, metadata is wired right | 🔴 Not Started |

**What you will learn:** the difference between a trace that *exists* and a trace that is *useful*; how cost accounting works in practice.

---

## Day 3 — Upload Golden Dataset, Run Eval via LangSmith

> Goal: the eval that lives in `data/eval/` is now a first-class LangSmith dataset, and we have LLM-as-judge evaluators.

| # | Task | Notes | Status |
|---|------|-------|--------|
| 3.1 | Upload `data/eval/golden_dataset.json` to LangSmith as dataset `golden-v1` | One-time via SDK script `scripts/upload_dataset.py` | 🔴 Not Started |
| 3.2 | Port `app/eval/metrics.py` functions into LangSmith evaluators (faithfulness, relevancy, keyword_hit, jargon_leak) | Ragas can be wrapped; custom ones become simple functions | 🔴 Not Started |
| 3.3 | Add an LLM-as-judge groundedness evaluator | Prompt: "given context + answer, is every claim supported? return 0-1" | 🔴 Not Started |
| 3.4 | Wire `scripts/run_eval.sh` to trigger a LangSmith experiment run | Replaces or wraps the existing Ragas runner | 🔴 Not Started |
| 3.5 | Verify: experiment results appear in LangSmith with per-example drill-down to traces | If you click a failing example and can see the full run tree, this is done | 🔴 Not Started |

**What you will learn:** why "dataset as code" loses to "dataset as managed artifact" once you have > 1 evaluator.

---

## Day 4 — Regression Gate

> Goal: no commit lands that silently degrades answer quality.

| # | Task | Notes | Status |
|---|------|-------|--------|
| 4.1 | Write `app/eval/diff.py` — loads current results, loads `baseline_results.json`, prints metric-by-metric delta | Human-readable table output | 🔴 Not Started |
| 4.2 | Add thresholds config: `faithfulness: -0.03`, `answer_relevancy: -0.03`, `jargon_leak_rate: +0.02` | Deltas are *allowed movements*, exceeding = fail | 🔴 Not Started |
| 4.3 | Add `scripts/check_regression.sh` — exits non-zero on gate failure | This is what CI calls | 🔴 Not Started |
| 4.4 | Add a pre-push git hook (optional) or a GitHub Action that runs `check_regression.sh` | Whichever the workflow tolerates | 🔴 Not Started |
| 4.5 | Deliberate-break test: intentionally regress `ANSWER_PROMPT`, confirm the gate fails | Critical — an untested gate is no gate | 🔴 Not Started |
| 4.6 | Update `data/eval/baseline_results.json` only via explicit commit with justification | Document this rule in `docs/observability.md` | 🔴 Not Started |

**What you will learn:** why "tests pass" is a weaker signal than "quality did not regress" in AI systems; how to design guardrails that fail loudly.

---

## Day 5 — Online Evaluators + Observability Doc

> Goal: production traffic is continuously graded; a new teammate can debug a bad answer in < 5 minutes using the docs.

| # | Task | Notes | Status |
|---|------|-------|--------|
| 5.1 | Configure a LangSmith online evaluator: sample 10% of runs in `move-mind-prod`, run the groundedness judge | Set up in UI, document the config in `docs/observability.md` | 🔴 Not Started |
| 5.2 | Create a LangSmith Monitor: alert (email or Slack) if rolling 24h faithfulness < 0.70 | Surfaces drift early | 🔴 Not Started |
| 5.3 | Write `docs/observability.md` — sections: Trace Anatomy, How to Debug a Bad Answer, Reading the Dashboard, Running Eval Locally, Interpreting the Regression Gate | Short, example-driven, screenshots OK | 🔴 Not Started |
| 5.4 | Dogfood the doc: pick one real failing run from earlier in the week, walk through the doc's debugging recipe, fix anything that trips you up | The doc is correct when you stop needing to edit it mid-walkthrough | 🔴 Not Started |
| 5.5 | Update `docs/system-audit.md` to mark observability items resolved | — | 🔴 Not Started |

**What you will learn:** the habit that separates mid-level from senior — shipping the docs that make *other people* (and future-you) productive on the system you just built.

---

## Deliverables Checklist (End of Week 2)

- [ ] LangSmith project `move-mind-dev` active, every run traced
- [ ] `data/eval/` still the source of truth; LangSmith dataset `golden-v1` mirrors it
- [ ] `scripts/run_eval.sh` writes result JSON + diffs against baseline
- [ ] `scripts/check_regression.sh` exits non-zero on drop, green on improvement
- [ ] `app/obs/pricing.py` + cost-per-run attribute on every trace
- [ ] Online groundedness judge active on 10% sample
- [ ] `docs/observability.md` complete and dogfooded
- [ ] `docs/system-audit.md` updated

---

## Skill Milestones (What "Senior" Looks Like After This Week)

Tick these when you can explain each unprompted:

- [ ] I can open any bad answer and within 5 minutes identify which node caused it
- [ ] I know the cost-per-query of our system to two decimals, and which node dominates it
- [ ] I can explain to a teammate why online eval is not a substitute for offline eval (or vice versa)
- [ ] I have a defensible answer to "why did you choose LangSmith over Langfuse"
- [ ] I know which metric I would watch to detect the single most likely production regression

---

## Week 3 Preview (Do Not Start Yet)

Once observability is in place, Week 3 introduces **agentic control flow**:

| Day | Focus |
|-----|-------|
| Day 1–2 | Document relevance grader node (CRAG pattern) — if docs are bad, loop to rewrite |
| Day 3 | Groundedness self-check node — if answer ungrounded, regenerate with stricter prompt |
| Day 4 | Route by `issue_type` — bug vs business_condition use different answer prompts |
| Day 5 | Measure lift: the regression gate from Week 2 confirms the new loops help, not hurt |

---

## Notes & Decisions

> Add pivots, blockers, or decisions here as the week progresses.

- **2026-04-14**: Week 2 plan locked. Observability chosen over agentic loops first — we need measurement before we can safely tune.
