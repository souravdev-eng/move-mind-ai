# LangSmith Integration — A Walkthrough

> **Teaching doc.** This explains *what* LangSmith does for us, *why* the code is shaped the way it is, and *how* each choice pays off. If you only need the runbook, skip to §9. If you want to understand the thinking, read top-to-bottom.
>
> Prerequisites: you've read the code in `app/obs/tracing.py` and `app/api/routes/chat.py` at least once.

---

## 0. The Problem We're Solving

Before any code: **why does observability deserve a whole module?**

In a classical web app, a 500 is a 500 and a 200 is a 200. The server tells you when it's wrong. LLM apps are different — the model returns a *confident, well-formatted* answer whether or not it's correct. The server says "200 OK" and the user reads a plausible hallucination. There's no exception to log, no stack trace to page on.

So we need a second layer of truth: for every answer, we want to see
1. **What went into it** — the question, the retrieved docs, the prompt.
2. **What came out of each step** — classifier decision, retrieval count, rerank winners, the final completion.
3. **What it cost** — tokens, dollars, wall-clock time.
4. **How it compared to what we expected** — evaluator scores against a golden dataset.

That's the job of the tracing + eval stack. Without it, debugging an LLM app is guessing. With it, every bad answer becomes a walk down a specific tree. The Google SRE book frames this as "observability buys you the ability to ask *new* questions about your system without re-deploying" — that's exactly what we're buying here.

**LangSmith** is the specific tool we picked to collect that telemetry. Why LangSmith and not, say, OpenTelemetry + Jaeger?

- Native LangChain / LangGraph integration — every `Runnable`, `@traceable`, and `.invoke()` already knows how to emit spans.
- The UI is purpose-built for LLM debugging: it shows prompts, completions, token counts, and cost per span. Jaeger won't do that.
- It doubles as an **experiment runner** — you upload a dataset, call `evaluate(...)`, get a scored comparison table. That one API eats two separate pieces of infra we'd otherwise have to build.

Trade-off we accepted: LangSmith is proprietary SaaS. If we outgrow it, porting out means rewriting the tracing adapter layer. That's OK because (a) the alternative is writing our own from scratch today, and (b) our own would take weeks and wouldn't have the UI. Pay now vs. pay more later — standard build-vs-buy.

---

## 1. The Mental Model (one paragraph)

Every call into the graph produces **one run tree**. The tree's root is the overall chat turn; its children are the nodes (`classify_question`, `retrieve_docs`, `rerank_docs`, `generate_answer`, …); leaves are the individual LLM calls, retriever calls, and tool calls inside those nodes. The tree is pushed to LangSmith, where each node carries its own structured metadata (`num_returned`, `cost_usd`, `latency_ms`, etc.). You debug a bad answer by opening the root, walking the tree, and finding the node where reality diverged from intent. You detect regressions by rerunning the same golden dataset and diffing evaluator scores between runs.

Everything in this doc is either (a) how we get the tree to be complete, (b) how we make sure it lands in the right place, or (c) how we tie it back to the code that produced it.

---

## 2. Trace Anatomy — one run, top to bottom

Here's what *one* chat turn looks like inside LangSmith:

```
root run: chat(question="why did CMS3 reject #1847?")
│  metadata: env=dev, session_id=..., cid=7093495, issue_type=bug,
│            cost_usd=0.018, latency_ms=3421, total_input_tokens=2104,
│            total_output_tokens=186, per_model={gpt-4o-mini: {...}, gpt-4o: {...}}
│  tags: env:dev, mode:manager, cid:7093495, issue:bug
│
├── classify_question                         [llm]
│   └── gpt-4o-mini                           ← actual LLM call
│       • prompt, completion, input_tokens, output_tokens
│
├── (rewrite_question — skipped this turn)
│
├── resolve_context                           [llm]
│   • metadata.active_customer_id=7093495    ← set by this node
│
├── retrieve_docs                             [retriever]
│   • metadata.k_summary=2, k_event=8, num_returned=10
│   ├── pinecone.similarity_search
│   └── bm25.similarity_search
│
├── rerank_docs                               [retriever]
│   • metadata.num_input=10, num_kept=5, cutoff=5
│   └── flashrank
│
├── generate_answer                           [chain]
│   └── gpt-4o  (or o3 if deep-reasoning)
│       • prompt includes top-5 reranked docs
│       • completion = the answer the user sees
│
└── classify_issue                            [llm]
    └── gpt-4o-mini
        • output: issue_type, confidence, reason
```

Three things are happening here that you should recognise in the code:

| What's happening | Mechanism | Where in code |
|---|---|---|
| Each node gets its own span | `@traceable(run_type=...)` decorator on the node function | `app/graphs/nodes/*.py` |
| Each node attaches structured data to its span | `attach_span_metadata({...})` helper | `app/obs/tracing.py:35` and called from retrieve/rerank nodes |
| Root run carries aggregates (cost, latency, cid, issue_type) | `invoke_with_observability` / `enrich_run_from_stream` post-patch the root run after the graph finishes | `app/obs/tracing.py:138`, `app/api/routes/chat.py:122` |

**Why split the work across `@traceable`, `attach_span_metadata`, and the post-patch step?** Because they run at different times:
- `@traceable` fires when the node *starts* and *ends* — it only knows the node's inputs and outputs.
- `attach_span_metadata` fires *inside* the node — when you know things like "Pinecone returned 10 docs."
- The post-patch (`_update_run`) fires *after* the whole graph finishes — only then do you know total cost, E2E latency, and every node's contribution.

Each layer captures what only it can see. That's the pattern to internalise.

---

## 3. Environment Routing — why three projects, not one

### The pain

You're on-call. Groundedness just dropped on the dashboard. You open LangSmith's "move-mind-ai" project to investigate, and you see:

- Your colleague's half-finished experiment from Tuesday (prompt had a typo — every answer was junk).
- Three eval runs against synthetic questions that don't reflect real traffic.
- The actual production traffic you care about.

All averaged together. The regression signal is drowned in noise you *created yourself*. You now have to manually filter by tags, in a panic, at 2 AM.

### The fix

Separate projects by environment, at capture time, so the signals never mix:

| `env` | Primary setting | Fallback | What lives there |
|---|---|---|---|
| `dev` | `LANGCHAIN_PROJECT_DEV` | `LANGCHAIN_PROJECT` | Local iteration. Noisy, fine. |
| `eval` | `LANGCHAIN_PROJECT_EVAL` | `LANGCHAIN_PROJECT` | Golden-dataset experiment runs. Clean by construction. |
| `prod` | `LANGCHAIN_PROJECT_PROD` | `LANGCHAIN_PROJECT` | Real user traffic. This is the one alerts fire on. |

Resolver: `Settings.langsmith_project_for(env)` in `app/config.py`. It's one `dict.get(env) or LANGCHAIN_PROJECT` — deliberately boring.

### How `env` flows through the code

```
build_run_config(env="dev")                 ← caller picks the env
  └── config["metadata"]["env"] = "dev"     ← stored on RunnableConfig
        │
        ▼
invoke_with_observability(graph, inputs, config)
  └── env = config["metadata"]["env"]       ← pulled back out
        │
        ▼
project_scope(env)                          ← returns context manager
  └── tracing_context(project_name=         ← langsmith SDK helper
        settings.langsmith_project_for(env))
        │
        ▼
  with project_scope(env), get_usage_metadata_callback() as cb:
      graph.invoke(...)                     ← runs inside both scopes
```

### Why `tracing_context`, not an env-var mutation?

A naive alternative: `os.environ["LANGCHAIN_PROJECT"] = "move-mind-eval"` right before invoking the graph. Two problems:

1. **Global mutation in a concurrent app is a footgun.** FastAPI serves requests concurrently. If request A flips the env var and request B reads it before A restores it, B's run lands in the wrong project. You just leaked test traffic into prod.
2. **It tells LangSmith's *client init* which project to use, not this specific invocation.** If the client was already constructed with the old value, setting the env var after the fact is ignored.

`langsmith.tracing_context(project_name=...)` is a scoped context manager the SDK provides specifically for this. It stores the project on a `ContextVar` (Python's async-safe per-task storage), which the tracer reads at span-creation time. Exit the `with` block → the override vanishes. No mutation survives the call.

**Pattern worth remembering:** when a library gives you a context-manager form of a global setting, prefer it over mutating the global. Context managers compose, roll back on errors, and are concurrency-safe.

### Why the fallback to a single `LANGCHAIN_PROJECT`?

Progressive disclosure. A new contributor clones the repo, fills in `LANGCHAIN_API_KEY`, and it just works — all runs go to `move-mind-ai`. They only opt into per-env projects when they actually need the separation. Zero-config to useful, one step at a time.

---

## 4. Experiment → Commit Correlation

### The pain

You run the eval on Tuesday. Score: `groundedness=0.82`. You run it Friday. Score: `groundedness=0.64`. **What changed?**

The UI tells you scores. It doesn't tell you *which commit produced those scores*. If you merged a dozen PRs between Tuesday and Friday — prompt tweaks, retriever settings, a model bump — you now have to bisect manually by re-running the experiment against each commit. That's minutes per rerun times a dozen commits. Miserable.

### The fix

Every experiment prefix now encodes the exact commit:

```
golden-v1-20260416-143022-7bf027a
           └─ timestamp ──┘ └ git short SHA
```

Now the debugging flow is:

1. Spot the regression in LangSmith's experiment list.
2. Copy the suffix SHA (`7bf027a`).
3. `git show 7bf027a` — read the commit.
4. `git log 7bf027a..HEAD` — see what landed after.
5. Usually the culprit is in those few commits.

### Why short SHA (7 chars), not full hash / branch / PR number?

- **Full hash**: too long, clutters experiment names, hurts sort order in the UI.
- **Branch name**: branches are mutable. `feat/eval` today points to a different commit next week. A SHA is immutable — it's the one thing that won't lie to you later.
- **PR number**: you don't have a PR number during local iteration. You want this to work before PR open.
- **Short SHA (7 chars)**: collision risk in a repo this size is effectively zero; git accepts it in every lookup; short enough to glance at. Defaults are usually defaults for a reason.

### Why the `nogit` fallback?

Docker images built in CI often don't include the `.git` directory (it bloats the image). If the script can't reach git, we'd rather substitute `"nogit"` and still record the experiment than crash on `subprocess.CalledProcessError`. The experiment name is slightly less useful; the run still happens. **Degrade gracefully, never lose data.**

---

## 5. Cost + Latency Capture (and why streaming is harder)

This is the most subtle part of the module. Read slowly.

### Why cost is not free to capture

LangSmith captures prompts and completions automatically (because it wraps the LangChain `Runnable`). Token counts are *returned by the model provider* on each call. But the **aggregation** — summing tokens across every LLM call in the graph and computing USD cost from per-model prices — is not automatic. You have to opt in.

LangChain exposes this via a callback:

```python
from langchain_core.callbacks.usage import get_usage_metadata_callback

with get_usage_metadata_callback() as cb:
    result = graph.invoke(inputs, config=config)

# cb.usage_metadata now holds:
# { "gpt-4o-mini": {"input_tokens": 1200, "output_tokens": 80, ...},
#   "gpt-4o":      {"input_tokens": 900,  "output_tokens": 106, ...} }
```

Inside the `with` block, every LLM call the graph makes notifies the callback. Exit the block → `cb.usage_metadata` is frozen and you can do arithmetic on it (→ `app/obs/pricing.py:cost_from_usage`).

**Why a callback, not a return value?** Because the graph doesn't know at invocation time how many LLM calls it'll make. A callback lets LangChain stream usage data as it happens, without forcing every intermediate function to carry it in its signature. Classic publisher-subscriber pattern — loose coupling between "who needs the data" (us) and "who produces it" (dozens of LLM calls deep inside the graph).

### Latency: just `time.perf_counter()`

No magic. Capture `t0` before `graph.invoke`, compute `latency_ms = (time.perf_counter() - t0) * 1000` after. Attach to root metadata. `time.perf_counter()` is monotonic (unaffected by wall-clock jumps, NTP, etc.) — that's the only reason we picked it over `time.time()`.

### Why streaming needed a second code path

The blocking path (`graph.invoke`) is the easy case:
1. Wrap the call in `get_usage_metadata_callback` and a timer.
2. When `invoke()` returns, you have the final `result` dict AND `cb.usage_metadata`.
3. Call `_update_run(run_id, metadata={cost, latency, cid, issue_type, ...})` once, done.

The streaming path (`graph.astream_events`) is fundamentally different:
1. `astream_events` is an **async generator** — it yields events as the graph progresses. It doesn't return a final dict; you assemble state by reading events.
2. You want to stream tokens to the browser as they're generated, so you can't block until the graph finishes before sending data.
3. You still need cost + latency at the *end* of the stream, to attach to the root run.

The pattern we landed on (see `app/api/routes/chat.py:122`):

```python
env = (config.get("metadata") or {}).get("env", "dev")
t0 = time.perf_counter()

with project_scope(env), get_usage_metadata_callback() as cb:
    async for event in graph.astream_events(..., config=config, version="v2"):
        # ... decode event, stream tokens to browser, accumulate state
        # cid, issue_type, query_type, etc. are pulled from events as they arrive

latency_ms = int((time.perf_counter() - t0) * 1000)

# Now the stream is done. cb.usage_metadata is populated. State is accumulated.
enrich_run_from_stream(run_id, state, cb.usage_metadata, latency_ms)
```

Two things to notice:

1. **The `async for` loop lives inside the `with` block.** That's what makes the callback capture usage across the whole stream. Exit the `with` block too early and you lose aggregation.
2. **State is accumulated from events.** `astream_events` gives us typed events like `on_chain_end` with a `name` field. We pattern-match on `name` to extract `active_customer_id` from `resolve_context`, `issue_type` from `classify_issue`, etc. The blocking path gets these in one `result` dict; the streaming path has to assemble them piece by piece.

### Why `enrich_run_from_stream` instead of extending `enrich_run_from_state`?

Original `enrich_run_from_state(run_id, state)` patched cid/issue/query_type onto the root run but knew nothing about cost or latency — it was designed for the streaming path before we added those captures.

When we added cost + latency, we had two options:

| Option | Verdict |
|---|---|
| A. Extend `enrich_run_from_state` with optional `usage_metadata` + `latency_ms` params | Rejected — grows the signature and creates two call sites with different argument shapes. "Just make it optional" is how you get 8-parameter functions over time. |
| B. Add a sibling function `enrich_run_from_stream` with the full shape the streaming path needs | Chosen — focused function, explicit about what it needs, cheap to delete if we ever unify. |

Two small functions > one function with half-used optional params. When in doubt, split.

---

## 6. How a Request Flows — end-to-end timeline

Following a single blocking `/api/v1/chat` request:

```
t=0ms   POST /api/v1/chat {question: "...", stream: false}
        │
        ▼
chat() in app/api/routes/chat.py:72
        │
        │ _run_config() → build_run_config(env="dev", ...)
        │   - generates run_id (UUID)
        │   - builds RunnableConfig with metadata={env, session_id, question_preview}
        │   - tags: env:dev, mode:manager
        │
        ▼
invoke_with_observability(graph, inputs, config, run_id=run_id)
        │
        │ env = config["metadata"]["env"]    → "dev"
        │ t0 = time.perf_counter()
        │
        │ ┌─────────────────────────────────────────────────────┐
        │ │ with project_scope("dev"),                          │
        │ │      get_usage_metadata_callback() as cb:           │
        │ │                                                     │
        │ │   # LangSmith now routes spans to "move-mind-dev".  │
        │ │   # cb is listening for every LLM call's usage.     │
        │ │                                                     │
        │ │   result = graph.invoke(inputs, config=config)      │
        │ │                                                     │
        │ │     │  Internally, LangGraph walks nodes:           │
        │ │     │   classify_question → (rewrite_question?) →   │
        │ │     │   resolve_context → retrieve_docs →           │
        │ │     │   rerank_docs → generate_answer →             │
        │ │     │   classify_issue                              │
        │ │     │                                               │
        │ │     │  Each node:                                   │
        │ │     │   - @traceable fires: span created            │
        │ │     │   - attach_span_metadata adds per-node data   │
        │ │     │   - LLM calls notify `cb`                     │
        │ │                                                     │
        │ └─────────────────────────────────────────────────────┘
        │
        │ latency_ms = int((perf_counter() - t0) * 1000)
        │
        │ usage_totals  = cost_from_usage(cb.usage_metadata)
        │ run_meta, tags = _enrichment_from_result(result)
        │ run_meta.update(usage_totals)
        │ run_meta["latency_ms"] = latency_ms
        │
        │ _update_run(run_id, metadata=run_meta, tags=tags)
        │   └── langsmith.Client().update_run(...)
        │           → PATCH against LangSmith API
        │
        ▼
t=3421ms  ChatResponse(...) → client
```

Nothing in this diagram is magic. Every step is a line of code you can open and read. The only "framework" part is `@traceable` + `attach_span_metadata` which talk to LangSmith's in-process tracer; everything else is plain Python.

---

## 7. Evaluators — current state and what they mean

Each LangSmith experiment runs `evaluate(target, data=DATASET_NAME, evaluators=ALL_EVALUATORS, ...)`. An evaluator is just a function:

```python
def keyword_hit_evaluator(run, example) -> dict:
    # run.outputs has what our graph produced
    # example.outputs has what the dataset says was expected
    return {"key": "keyword_hit", "score": 0.83, "comment": "..."}
```

The score shows up as a column in the experiment UI. You can sort experiments by it, alert on it, and track it over time.

| Evaluator | Key | What it measures | How |
|---|---|---|---|
| `keyword_hit_evaluator` | `keyword_hit` | Fraction of expected keywords in the answer | String match against `example.expected_keywords` |
| `jargon_leak_evaluator` | `jargon_leak` | Fraction of blocked technical terms in the answer (lower is better) | String match against a curated blocklist |
| `groundedness_evaluator` | `groundedness` | Is every claim in the answer supported by the retrieved context? | LLM-as-judge — we ask a smaller model to grade the answer against the docs |

**Why a mix of string-match and LLM-judge?** Different metrics catch different failures:

- String-match is **cheap and deterministic**. Same inputs → same score. Great for invariants ("the answer should mention the customer_id they asked about").
- LLM-judge is **semantic**. It catches "the answer says X but the docs say Y" where no keyword list could. Expensive (it's another LLM call per example) and non-deterministic, but it's the only way to measure groundedness without human labelling.

We use both because they fail in different ways. If an answer scores high on string-match but low on groundedness, it probably has the right words in the wrong relationships — a classic hallucination signature.

Phase 3/4 of `docs/tracking/eval-tracing-plan.md` adds four more: `faithfulness_ragas`, `answer_relevancy_ragas`, `latency_evaluator`, `non_technical_clarity_evaluator`.

---

## 8. The Regression Gate (how experiments become a safety net)

Running experiments is valuable. Running experiments + comparing to a baseline = regression detection. That's `app/eval/diff.py` + `scripts/run_eval.sh`.

Workflow:

1. Today's eval writes `data/eval/latest_results.json`.
2. `diff.py` compares it against `data/eval/baseline_results.json` metric-by-metric.
3. Each metric is classified `OK`, `WARN`, or `FAIL` based on drift budget (`GATE_CONFIG` in `diff.py`).
4. CI (or you, locally) fails the build on `FAIL`. `WARN` is a yellow light — worth investigating, not a blocker.

**Why budgets instead of strict inequality?** LLM metrics are noisy. Groundedness bouncing 0.82 → 0.81 between runs with no code change is normal — different sampling, temperature, etc. A strict "must not decrease" gate would page on noise. A drift budget (e.g. "0.03 is allowed") separates signal from noise. Tune the budget tight enough that real regressions can't hide, loose enough that normal variance doesn't page you. This is the same trade-off you'd make on a latency SLO.

**Updating the baseline is an explicit, committed action.** The commit message is the record of *why* the baseline moved. "answer prompt rewrite improved faithfulness 0.64 → 0.71, baseline refreshed" is a valid reason. "updating baseline" is not — because if next week groundedness is 0.61 we've lost the thread of why 0.71 was OK.

---

## 9. Runbook — Use It Yourself

### First-time setup

```bash
# 1. Copy .env and fill in the LangSmith fields
cp .env.example .env
# edit:
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=ls_...
#   LANGCHAIN_PROJECT_DEV=move-mind-dev
#   LANGCHAIN_PROJECT_EVAL=move-mind-eval
#   LANGCHAIN_PROJECT_PROD=move-mind-prod

# 2. Upload the golden dataset (idempotent — safe to rerun)
uv run python scripts/upload_dataset.py

# 3. Full eval (offline metrics + LangSmith experiment + regression gate)
bash scripts/run_eval.sh

# 4. Offline-only (skip LangSmith network calls)
bash scripts/run_eval.sh --skip-langsmith

# 5. Accept today's results as the new baseline (do this deliberately)
bash scripts/run_eval.sh --update-baseline
```

### Debugging a bad answer (<5 min target)

1. LangSmith → `move-mind-dev` project.
2. Filter by `tags:cid:<customer_id>` or search on `question_preview`.
3. Open the root run. Eyeball `cost_usd` + `latency_ms` — anything wildly off?
4. Walk the tree top-down using the table in §2. First node whose metadata surprises you = root cause.
5. If nothing's surprising but the answer is wrong, open `generate_answer`'s LLM span and read the prompt + completion. Hallucinations live there.

### Reading an experiment

1. LangSmith → `move-mind-eval` → Experiments tab.
2. Sort by the metric you care about (e.g. `groundedness` descending).
3. Compare today's run to last week's. If scores dropped, read the SHA suffix → `git show <sha>` → find the commit.
4. Click into an example with a low score to see the actual answer + retrieved docs.

---

## 10. Common Confusions

| Confusion | Clarification |
|---|---|
| "Isn't `cost_usd` automatic?" | No. LangSmith captures prompts/completions for free but aggregating tokens + multiplying by per-model price is ours to do. See `app/obs/pricing.py`. |
| "Why do I see `cost_usd=0.0` on a streamed run?" | The SSE generator's `astream_events` loop must be *inside* `get_usage_metadata_callback`. If it isn't, the callback never sees the LLM calls. |
| "Why does the experiment name have `nogit` in it?" | `git rev-parse` failed — usually a detached HEAD or a build environment without `.git`. Not a bug; we fall back rather than crash. |
| "Why is my run in `move-mind-ai` instead of `move-mind-dev`?" | `LANGCHAIN_PROJECT_DEV` is unset, so the resolver fell back to `LANGCHAIN_PROJECT`. Check `.env`. |
| "Can I add per-node metadata from a new node I'm writing?" | Yes — `from app.obs.tracing import attach_span_metadata` and call it inside the node function after the `@traceable` decorator is applied. Use flat dicts (LangSmith doesn't nest well). |
| "What's the difference between `groundedness` and `faithfulness`?" | Same concept, different implementations. `groundedness_evaluator` is our LLM-judge. `faithfulness` (planned) is Ragas's implementation. We'll keep both — they'll be named `groundedness_llm_judge` and `faithfulness_ragas` so the distinction is obvious. |

---

## 11. Further Reading (from your own shelf)

- **SRE book, ch. "Monitoring Distributed Systems"** — the four golden signals (latency, traffic, errors, saturation). Our `latency_ms` + `cost_usd` + evaluator-fail-rate are the LLM equivalents.
- **DDIA, ch. 10 "Batch Processing"** — mental model for experiments-as-batch-jobs over a golden dataset.
- **LLMOps book, ch. on evaluation** — the faithfulness/answer-relevancy/context-precision/context-recall quartet is straight from Ragas, which builds on research surveyed there.
- **LLM Security book** — prompt injection via retrieved docs is a real threat; the groundedness judge is also a weak defense-in-depth signal ("did the model follow an instruction it read in a retrieved doc?").

---

## 12. What's Next

Phase 3 + 4 (`docs/tracking/eval-tracing-plan.md`): full metric set — `context_precision`, `context_recall`, `latency_ms`, `classification_accuracy`, `non_technical_clarity` — plus LangSmith evaluators for all of them. Phase 5: archive the stale `data/eval_results.json`, run a clean baseline, configure the LangSmith online evaluator + monitor for production traffic.

When each lands, an `eval-pipeline.md` sibling doc will teach the metric definitions the same way this one teaches tracing.
