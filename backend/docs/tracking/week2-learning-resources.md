# Week 2 — Learning Resources (Visual Learner Path)

> Companion to `docs/tracking/week2-plan.md`. For each concept in Part A and each task in Part B, this doc gives you:
> - **Stack** — exact package / SDK / CLI to install and use
> - **Docs** — the one canonical page to bookmark
> - **YouTube search queries** — type these verbatim into YouTube; sort by "This year" for freshness
> - **Udemy / DeepLearning.AI courses** — the short, high-signal ones
> - **Verify you learned it** — a 1-line self-test

Rule of thumb for AI topics on YouTube: anything older than ~12 months on LangChain / LangGraph / LangSmith is likely **outdated API**. Always sort by upload date.

---

## Our Week 2 Stack (Install Once)

```bash
# Core tracing / eval
pip install langsmith                 # tracing backend
pip install "langchain>=0.3"          # already in repo
pip install "langgraph>=0.2"          # already in repo
pip install ragas                     # offline eval metrics (already in repo)

# Supporting
pip install tiktoken                  # token counting for cost calc
pip install python-dotenv             # env loading (already in repo)
```

**Alternatives you do NOT need to install, but should know exist** (for the "why LangSmith?" interview answer):
- **Langfuse** — OSS self-hosted alternative to LangSmith
- **Arize Phoenix** — OSS, stronger on embedding drift
- **OpenTelemetry + Grafana** — vendor-neutral, more plumbing
- **Helicone** — proxy-based, simpler but less LangGraph-native

---

## Part A — Concepts, Mapped to Resources

### A.1 — Tracing vs Logging vs Metrics vs Evaluation

**Stack:** conceptual only; no install.

**Canonical reading (20 min):**
- Google SRE Book — chapter "Monitoring Distributed Systems" (free online). The "four golden signals" idea transfers directly.

**YouTube searches:**
- `observability vs monitoring explained`
- `traces logs metrics three pillars`
- `LLM observability vs traditional observability`

**Course:**
- DeepLearning.AI — **"Quality and Safety for LLM Applications"** (short course, free). Covers the eval side cleanly.

**Verify you learned it:** in one sentence each, explain why a trace alone cannot tell you if quality regressed, and why an aggregate metric alone cannot tell you *which run* caused the regression.

---

### A.2 — The Run Tree (Spans and Parent/Child)

**Stack:** `langsmith` SDK — the `@traceable` decorator and the automatic LangChain/LangGraph instrumentation.

**Canonical docs:**
- `docs.smith.langchain.com` → "Tracing" → "Trace with @traceable / Runnable"
- `python.langchain.com` → "LangGraph" → "How-to: add tracing"

**YouTube searches:**
- `LangSmith tracing tutorial`
- `LangSmith LangGraph tracing`
- `OpenTelemetry spans explained` (for the general theory)

**Channels that cover this well** (search the channel name + "LangSmith"):
- **LangChain** (official) — their "LangSmith" playlist
- **Sam Witteveen**
- **James Briggs**
- **AI Makerspace**

**Verify you learned it:** open your LangSmith UI after Day 1. Can you point at the exact span where `rerank_docs` called Cohere, and read the input + output + latency off that span?

---

### A.3 — LangSmith (Our Chosen Backend)

**Stack:** `langsmith` Python SDK + LangSmith cloud (free tier).

**Canonical docs (bookmark all three):**
- `docs.smith.langchain.com` — concepts
- `docs.smith.langchain.com/evaluation` — datasets + evaluators
- `docs.smith.langchain.com/observability` — tracing + monitors

**YouTube searches:**
- `LangSmith tutorial 2025` (freshness matters — API changed)
- `LangSmith datasets evaluators`
- `LangSmith online evaluator`
- `LangSmith monitor alerts`

**Course:**
- **LangChain Academy** (free, on their site + YouTube) — "Introduction to LangSmith" and the "Evaluation" modules. This is made by the LangSmith team itself and is the single highest-signal resource.

**Verify you learned it:** without opening the docs, can you describe the difference between a `Project`, a `Dataset`, and an `Experiment` in LangSmith?

---

### A.4 — Tokens, Cost, and Latency Attribution

**Stack:** `tiktoken` (token counting) + `langsmith` (captures token counts automatically on LangChain LLM calls).

**Canonical reading:**
- OpenAI pricing page (bookmark; memorize gpt-4o, gpt-4o-mini, o3-mini rates)
- `platform.openai.com` → docs → "Tokens" explainer

**YouTube searches:**
- `LLM cost optimization production`
- `tiktoken tutorial python`
- `p50 p95 p99 latency explained`

**Course:**
- **DeepLearning.AI — "Building Systems with the ChatGPT API"** covers token accounting early on.

**Verify you learned it:** for one full run of `investigate_cid("CID-123")`, can you state — without guessing — total input tokens, total output tokens, and total cost in USD? (After Day 2 you should.)

---

### A.5 — Online Evaluators vs Offline Eval

**Stack:** `ragas` (offline, already in repo) + LangSmith online evaluators (UI + SDK).

**Canonical docs:**
- `docs.ragas.io` — metric definitions (faithfulness, answer_relevancy, context_precision, context_recall)
- `docs.smith.langchain.com/evaluation/how_to_guides/online_evaluations`

**YouTube searches:**
- `Ragas RAG evaluation tutorial`
- `LLM as judge evaluation`
- `online evaluation LLM production`

**Course (the single best one for this week):**
- **DeepLearning.AI — "Building and Evaluating Advanced RAG"** (taught with LlamaIndex but the eval concepts are identical). Free, ~1 hour. Covers Ragas metrics, LLM-as-judge, the why behind each.

**Verify you learned it:** give a scenario where offline eval is green but online eval catches a regression. (Hint: changing retrieval corpus.)

---

### A.6 — Regression Gates

**Stack:** pure Python (`app/eval/diff.py`) + git hooks or GitHub Actions.

**Canonical reading:**
- Martin Fowler — "Continuous Integration" essay (classic, still the clearest articulation)
- GitHub Actions docs — "Quickstart" (for the CI wiring)

**YouTube searches:**
- `GitHub Actions python pytest tutorial`
- `pre-commit hooks python`
- `ML model regression testing CI`

**Verify you learned it:** can you intentionally regress `ANSWER_PROMPT`, run your gate, and watch it block you? (This *is* Day 4 Task 4.5.)

---

### A.7 — Failure Modes of RAG

**Stack:** conceptual; surfaced through your Ragas + LangSmith dashboards.

**YouTube searches:**
- `RAG failure modes`
- `Corrective RAG CRAG paper explained`
- `Self-RAG paper explained`
- `hallucination detection LLM`

**Papers (skim, don't read deeply — watch the paper-walkthrough videos instead):**
- "Corrective Retrieval-Augmented Generation" (CRAG, 2024)
- "Self-RAG: Learning to Retrieve, Generate, and Critique" (2023)

**Channels for paper walkthroughs:**
- **Yannic Kilcher**
- **AI Coffee Break with Letitia**
- **1littlecoder**

**Verify you learned it:** given a bad answer, name three distinct root causes and how each would show up differently in the trace.

---

## Part B — Tasks, Mapped to Resources

> For each day's tasks in `week2-plan.md`, here is the exact thing to watch / read **before** you start coding.

### Day 1 — Wire LangSmith Tracing

**Watch first (in this order):**
1. YouTube: `LangSmith getting started 2025` — pick a video ≤ 6 months old, ≥ 10 min, from LangChain official channel if available
2. Docs: `docs.smith.langchain.com` → "Quick Start"

**You need to know:**
- What `LANGCHAIN_TRACING_V2=true` does under the hood (env-var toggle that LangChain's internal callbacks check)
- Why LangGraph + LangChain traces auto-instrument but raw functions need `@traceable`

**Gotchas:**
- Traces from `.env` won't fire if you import LangChain before dotenv loads. Load env first.
- Free tier has a monthly trace limit — enough for dev, watch it if you batch-run eval.

---

### Day 2 — Enrich Traces

**Watch first:**
- YouTube: `LangSmith metadata tags filtering`
- YouTube: `RunnableConfig LangChain tutorial`

**You need to know:**
- `RunnableConfig` — how to pass `metadata={}` and `tags=[]` down the graph
- How token usage propagates from an OpenAI call up to the enclosing span (automatic in LangChain, manual elsewhere)
- Cost calculation pattern: keep a `{model_name: (price_in_per_1m, price_out_per_1m)}` dict and a helper that reads the span's token usage

**Gotchas:**
- Not every model provider reports token usage the same way. Verify for each model you use.

---

### Day 3 — Upload Dataset, LangSmith Evaluators

**Watch first:**
- YouTube: `LangSmith evaluation tutorial` (LangChain official)
- LangChain Academy: "Evaluation" module (free, on YouTube and langchain.com/academy)

**You need to know:**
- `Client.create_dataset` + `Client.create_examples` API
- The shape of a LangSmith evaluator: `def my_eval(run, example) -> {"key": ..., "score": ...}`
- Wrapping Ragas metrics into this shape

**Gotchas:**
- Running an experiment re-runs your graph on every example. Expect to burn real tokens — budget for it.

---

### Day 4 — Regression Gate

**Watch first:**
- YouTube: `pytest parametrize tutorial` (if unfamiliar)
- YouTube: `github actions python tutorial 2025`

**You need to know:**
- How to read two JSON files, diff their top-level metrics, and exit non-zero on breach
- How to wire a single script to both a local git hook and a GitHub Action

**Gotchas:**
- Flaky LLM evals can breach thresholds randomly. Either run N times and average, or set thresholds with a noise buffer.

---

### Day 5 — Online Eval + Observability Doc

**Watch first:**
- YouTube: `LangSmith online evaluation production`
- YouTube: `LangSmith monitoring alerts`

**You need to know:**
- How sampling works (10% is a config, not code)
- How to write a "debug recipe" doc: screenshot + numbered steps + expected UI state

**Gotchas:**
- A great observability doc is *dogfooded* — if you can't debug a known bad run using only your own doc, the doc is wrong.

---

## Courses to Finish in Parallel This Week (Pick 1–2)

| Course | Where | Length | Why |
|--------|-------|--------|-----|
| **LangChain Academy — Introduction to LangSmith** | langchain.com/academy (free) | ~2 hours | Direct hit on our stack |
| **DeepLearning.AI — Building and Evaluating Advanced RAG** | deeplearning.ai (free) | ~1 hour | Best eval concepts, vendor-neutral |
| **DeepLearning.AI — Quality and Safety for LLM Applications** | deeplearning.ai (free) | ~1 hour | Covers LLM-as-judge cleanly |
| **Udemy — any "LangChain LangGraph production"** | Udemy (paid) | varies | Only if the free ones leave gaps; always check upload year < 1 |

**Ignore:** any course older than 2024 that claims to cover LangChain "comprehensively". The API broke too many times.

---

## YouTube Channels Worth Subscribing To

- **LangChain** (official) — authoritative for our exact stack
- **AI Engineer** (conference channel) — talks from people running this in prod
- **Sam Witteveen** — practical, weekly, stays current
- **James Briggs** — RAG + vector search deep-dives
- **Greg Kamradt (Data Independent)** — LLM app patterns, solid foundations
- **AI Makerspace** — live-coded walkthroughs, beginner-friendly pace
- **Yannic Kilcher** — when you want the paper, not the tutorial

---

## How to Recognize "Which Topic Do I Need" Going Forward

When you hit a wall this week, the pattern is:

1. **What am I trying to see?** (A log line? A metric over time? A comparison against a baseline?)
2. **Which of the four signals is that?** (log / metric / trace / eval)
3. **Which part of our stack owns that signal?** (LangSmith trace? Ragas eval? Custom log?)
4. **Search query = `<tool name> <exact feature> tutorial 2025`.**

This is the question-decomposition habit that Senior AI engineers run on autopilot. Practice it this week.

---

## Notes

> Track what worked (which video / course actually taught you the thing) so Week 3 planning uses the same muscle.

- (fill in as you go)
