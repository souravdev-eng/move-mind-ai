# Observability — A Walkthrough

> **Teaching doc.** This explains *why* we observe the system the way we do, *what* the signals mean, and *how* to use them to find root causes fast. If you want the plumbing (env routing, tracing context, callbacks), read [`langsmith-integration.md`](./langsmith-integration.md) first — this doc assumes you've seen it.
>
> **Scope split.**
> - `langsmith-integration.md` = how signals get captured.
> - `observability.md` (this doc) = how humans use those signals.
> - `eval-pipeline.md` = how we measure quality over time against a golden dataset.

---

## 0. What "Observability" Means Here

A useful distinction from the SRE book:

- **Monitoring** tells you *a thing you already knew to worry about* has crossed a threshold. CPU > 80%. 5xx rate > 1%. You defined the alert ahead of time.
- **Observability** lets you ask *new* questions about your system without shipping new code. "Why did this specific answer mention the wrong customer?" — a question you didn't anticipate, answered from data that was captured anyway.

Traditional web apps lean on monitoring (four golden signals: latency, traffic, errors, saturation). LLM apps need observability much more, because the failure modes are **semantic, not numeric**:

- The server returned a 200. Latency was fine. Cost was fine. The answer was wrong.
- That failure doesn't trigger any monitor. The *only* way to catch it is to walk the trace of what happened and notice that the retrieval was thin, or the prompt didn't include the right context, or the model ignored a critical doc.

So observability in this repo is *explicitly designed to let you answer "why did the assistant give that answer?" in under 5 minutes* — which is the single most important debug loop we have.

### The mental model — one paragraph

Every chat turn emits a **run tree** in LangSmith. The root is the request; its children are the graph nodes; the leaves are the actual LLM and retriever calls. Each node decorates its own span with structured metadata about what it did (`num_returned`, `num_kept`, `issue_type`, etc.). You debug by opening the root, walking the tree top-down, and stopping at the first node whose metadata disagrees with your expectation — that's usually the bug.

---

## 1. Trace Anatomy — what each span tells you

A typical blocking request produces this tree. Skim it once, then read the notes below:

```
root run: chat(question="...")                     [env=dev, cost_usd=0.018, latency_ms=3421]
│
├── classify_question           [llm]              decides: "retrieve" vs "rewrite"
│   └── gpt-4o-mini                                prompt + completion visible in UI
│
├── (rewrite_question)          [llm]  optional    only runs when classifier says "rewrite"
│   └── gpt-4o-mini
│
├── resolve_context             [llm]              sets active_customer_id / active_page_path
│
├── retrieve_docs               [retriever]        k_summary, k_event, num_returned
│   ├── pinecone.similarity
│   └── bm25.similarity
│
├── rerank_docs                 [retriever]        num_input, num_kept, cutoff
│   └── flashrank
│
├── generate_answer             [chain]            the prompt + the answer live here
│   └── gpt-4o  (or o3 for deep-reasoning)
│
└── classify_issue              [llm]              issue_type, issue_confidence, reason
    └── gpt-4o-mini
```

### What you should learn to read at a glance

| Span | Metadata to eyeball | What it tells you |
|---|---|---|
| **Root run** | `latency_ms`, `cost_usd`, `cid`, `issue_type`, `query_type` | One-line health of the whole turn. If any of these is surprising, drill down. |
| **classify_question** | `query_type` in output | Did we route to `retrieve` (new question) or `rewrite` (vague follow-up)? Wrong routing = downstream retrieval uses a stale question. |
| **resolve_context** | `active_customer_id` in output | The CID the system locked onto. If empty, retrieval has nothing to filter on — answers get generic. |
| **retrieve_docs** | `num_returned` | Zero = retrieval miss (almost always the cause of "I couldn't find anything"). 1–3 = thin evidence. |
| **rerank_docs** | `num_input`, `num_kept`, `cutoff` | `num_kept` is the count that actually reaches the LLM. Low `num_kept` with high `num_input` = the reranker dropped everything below cutoff. |
| **generate_answer** | LLM span → prompt + completion | Open this when the answer is wrong. The prompt shows exactly what context the LLM had; the completion shows what it did with it. Hallucinations live here. |
| **classify_issue** | `issue_type`, `issue_confidence` | If `unknown` with high-information context, the classifier prompt needs work. |

### Why metadata is attached at the node, not accumulated at the root

It would be tempting to collect everything at the root run and forget about per-node metadata. We don't, because **each value is only meaningful next to the span that produced it**:

- `num_returned=10` on the root is ambiguous — returned by whom?
- `num_returned=10` on the `retrieve_docs` span is a fact about retrieval you can act on.

Putting metadata at the right level means you can filter in the UI (`retrieve_docs.num_returned = 0`) and spot an entire class of failures without loading any individual run. That's the payoff.

---

## 2. The 5-Minute Debug Workflow

This is the whole point of the trace stack. Drill it until it's muscle memory.

### Step-by-step

1. **Find the run.** LangSmith → `move-mind-dev` (or prod) → filter:
   - By customer: `tags:cid:<customer_id>`.
   - By question: search `question_preview`.
   - By symptom: `metadata:issue_type:unknown` or `metadata:cost_usd > 0.05`.
2. **Eyeball root metadata.** `latency_ms`, `cost_usd`, `cid`, `issue_type`. Anything wildly off is a tell on its own.
3. **Walk the tree top-down.** At each node, ask: *does this metadata match what I expected?* Stop at the first mismatch.
4. **Open the offending span.** For nodes with LLM calls, read the prompt and the completion. For retriever nodes, read the retrieved document contents.
5. **Form a hypothesis, check it, fix it.** Usually the hypothesis is "the LLM was given X and produced Y — a prompt or retrieval change would flip this."

### Common failure fingerprints

| Symptom | Likely span | How to confirm |
|---|---|---|
| Confidently wrong answer | `generate_answer` | Prompt had the right context; completion ignored it. Groundedness will be low. |
| "I couldn't find anything" | `retrieve_docs` or `resolve_context` | `num_returned = 0` OR `active_customer_id` was never set. |
| Answer mixes two customers | `resolve_context` (session turn-to-turn) | CID changed between this turn and the prior turn in the same thread. |
| Answer uses raw log jargon ("decision_result", "gql_…") | `generate_answer` prompt | Prompt template leaked field names; `jargon_leak_rate` will be high on the next eval. |
| Latency > 10s | `rerank_docs` duration + LLM span in `generate_answer` | Reranker slow, or model escalated to `o3`. |
| Cost > $0.05 | `per_model` on root | `o3` likely triggered; check whether the question actually needed deep reasoning. |
| `issue_type = unknown` on a clearly-described bug | `classify_issue` LLM span | Prompt likely didn't give the classifier enough context — open the span and see what it received. |

### Why a 5-minute target?

Debug loops determine how often you actually debug. If "why did this answer go wrong?" takes 30 minutes, you'll look at maybe two bad answers a week. If it takes 5 minutes, you'll look at twenty. **The faster the loop, the tighter the feedback — and tight feedback is how quality compounds.** This is straight out of "Accelerate" (Forsgren et al.) and echoes Brooks's old observation that programmers pay more for debugging than for writing code.

---

## 3. Dashboard Filters Worth Saving

In LangSmith, filters compose. These are the ones that earn their keep:

| Filter | What it shows | When to use |
|---|---|---|
| `tags:env:dev` | Only local runs | Daily iteration — keeps prod noise out. |
| `tags:cid:<id>` | One customer's runs across turns | When a manager says "the assistant got this wrong for customer X". |
| `tags:issue:bug` | Runs the classifier labelled as bugs | Sampling the bug-triage surface specifically. |
| `metadata:retrieve_docs.num_returned = 0` | Retrieval misses | Find questions where the vector store had nothing. Often means ingestion or embedding mismatch. |
| `metadata:rerank_docs.num_kept < 2` | Thin-evidence runs | High chance of hallucination — worth manual review. |
| `metadata:cost_usd > 0.05` | Cost outliers | Usually `o3` escalations. Check if they were warranted. |
| `metadata:latency_ms > 10000` | Latency outliers | `rerank_docs` or `o3` LLM span is almost always the culprit. |
| LLM span with `model = o3` | Every deep-reasoning escalation | Spot-check whether the question really needed `o3`. |

**Tip:** save these filters as named views in LangSmith so you don't re-type them every session.

---

## 4. The Signals — and why we capture each

Four categories of signal live on every run. Understanding *why* each exists helps you know which one to reach for.

### 4.1 Cost (`cost_usd`, `total_input_tokens`, `total_output_tokens`, `per_model`)

**Why capture cost?** Because LLM cost is a per-request variable, not a fixed operational cost. One stray `o3` call can cost more than a week of `gpt-4o-mini` calls. Without cost visibility, you can't (a) budget, (b) spot regressions in model routing, or (c) make an informed choice when a prompt change trades quality for tokens.

**How it's captured.** `langchain_core.callbacks.usage.get_usage_metadata_callback` is a context manager. Everything that happens inside it reports token usage to the callback. After the block exits, we call `cost_from_usage()` in `app/obs/pricing.py` to multiply token counts by per-model prices. The result goes onto the root run as `cost_usd` + a `per_model` breakdown.

**What `per_model` buys you.** When cost spikes, you don't want to know "cost_usd went up by 3¢" — you want to know *which model drove it*. `per_model` is that breakdown. Example: `{"gpt-4o": {input_tokens: 800, cost: 0.002}, "o3": {input_tokens: 1200, cost: 0.030}}` tells you instantly that `o3` was the spike.

### 4.2 Latency (`latency_ms`)

**Why capture latency at the root, not just individual LLM spans?** Because E2E latency is what the user actually experiences. LangSmith records per-span durations automatically (useful for tuning a slow node), but the *user's* latency is `sum(all spans) + graph overhead`. We measure that explicitly with `time.perf_counter()` around the graph invocation in `invoke_with_observability` and around the `astream_events` loop in the streaming handler.

**Why `perf_counter`, not `time.time`?** `perf_counter` is monotonic — it can't go backwards from NTP adjustments or clock changes. For "how long did this take" measurements, monotonic is the right clock. `time.time` is for "what time did this happen" (wall clock).

### 4.3 Identifiers (`cid`, `session_id`, `thread_id`, `query_type`, `issue_type`)

**Why capture these?** Because the questions you'll ask in a week are "what happened for customer X" and "what did the assistant think about bug-type questions yesterday". You can only ask those if the identifiers are already on the runs.

**Where they come from.**
- `cid` / `active_customer_id` — set by `resolve_context`, promoted to the root run by `_enrichment_from_result`.
- `session_id` / `thread_id` — the LangGraph thread, identical across turns of a conversation. Key for "what did the assistant say over a multi-turn conversation."
- `query_type` — output of `classify_question` (`retrieve` or `rewrite`).
- `issue_type` / `issue_confidence` — output of `classify_issue`.

**Why tags too, not just metadata?** LangSmith lets you filter by both, but tags are optimised for fast lookup (`tags:cid:7093495` is O(index)). Duplicating onto tags lets us keep the dashboard filters snappy while still having the full metadata for drill-down.

### 4.4 Per-node structured metadata

Added inside the node via `attach_span_metadata({...})`:

| Node | Metadata | Why we care |
|---|---|---|
| `retrieve_docs` | `k_summary`, `k_event`, `num_returned`, `analysis_mode` | Tells you how hard we tried (`k_*`) and what came back (`num_returned`). A retrieval that returned 0 with `k_event=8` is a very different story from one that returned 8 out of 8. |
| `rerank_docs` | `num_input`, `num_kept`, `cutoff`, `bypass_reason` (sometimes) | Did the reranker thin the evidence? If `num_kept=1` and `num_input=10`, 9 docs looked irrelevant to FlashRank — possibly correct, possibly a tuning issue. |
| `classify_issue` | `issue_type`, `issue_confidence` | Lets you slice the dashboard by issue type without opening every run. |

---

## 5. Debug Runbook — full recipe

Copy-pasteable for the next time something goes wrong.

### Recipe A: "The assistant said something wrong. Why?"

1. Get the `cid` or the exact question from the user who reported it.
2. LangSmith → `move-mind-dev` (or `-prod`) → filter `tags:cid:<cid>` + sort by time descending.
3. Open the root run for that turn.
4. Quick scan:
   - `active_customer_id` set? If not → `resolve_context` is the bug.
   - `num_returned > 0`? If not → retrieval miss; check ingestion.
   - `num_kept >= 2`? If not → thin evidence; check rerank thresholds.
5. If all structural checks pass, open `generate_answer`'s LLM span and read the prompt + completion side by side.
6. Form the hypothesis — usually one of:
   - "Prompt didn't have the relevant doc" → fix retrieval or rerank.
   - "Prompt had it; model ignored it" → fix prompt (add explicit instruction) or escalate model.
   - "Model confabulated" → fix prompt (constrain style) or tighten the groundedness judge.
7. Reproduce locally; patch; add a question to the golden dataset so it's caught in eval next run.

### Recipe B: "Something is slow. What?"

1. LangSmith → filter `metadata:latency_ms > 10000`.
2. Open one. Look at per-span durations in the tree.
3. Usually one of:
   - `rerank_docs` > 2s → FlashRank is slow; check model size or document count.
   - `generate_answer` LLM span > 8s → likely `o3` escalation. Check root `per_model`.
   - `retrieve_docs` > 2s → Pinecone latency or BM25 rebuild.

### Recipe C: "Cost is up this week."

1. LangSmith → filter `metadata:cost_usd > 0.05`, group by day.
2. Open a high-cost run. Check `per_model`.
3. `o3` present → look at the question; was deep reasoning actually needed? If not, tune the escalation trigger (`app/graphs/nodes/generate_answer.py`).
4. Lots of `gpt-4o` cost → probably a prompt got longer. Diff the `generate_answer` prompt template over time.

---

## 6. Online Evaluation (status: pending)

Once production traffic exists (see `docs/tracking/week2-plan.md`), set up a LangSmith **online evaluator**:

- Sample 10% of runs in the `move-mind-prod` project.
- Apply the `groundedness_evaluator` (LLM-as-judge) to each sampled run.
- Store the score on the run as feedback.
- Configure a LangSmith **Monitor** to alert if the rolling 24h `groundedness` drops below 0.70.

### Why an online evaluator in addition to the golden-dataset eval?

Two different failure modes:

| Mechanism | Catches | Misses |
|---|---|---|
| Golden-dataset eval (batch, pre-merge) | Regressions against a fixed, representative set of questions | Novel questions in prod that the golden set never anticipated |
| Online evaluator (sampled, continuous) | Quality drops on *actual* prod traffic as it evolves | Systematic gaps in a specific category (because it samples randomly) |

You want both. Batch eval is a regression gate — it protects the known world. Online eval is a canary — it flags when reality drifts away from the known world. This is the LLM version of "unit tests + production monitoring"; neither replaces the other.

**Why sample 10%, not 100%?** The evaluator is an LLM call per sampled run. 100% sampling doubles your LLM spend. 10% is enough to detect a statistically meaningful drop (~0.03 on a 100/day traffic base) without doubling the bill. Tune up if signal is too noisy.

---

## 7. Troubleshooting Observability Itself

When the trace stack misbehaves, the problem is almost always one of these:

| Problem | Check |
|---|---|
| No traces appearing in LangSmith | `LANGCHAIN_TRACING_V2=true` in `.env`? `LANGCHAIN_API_KEY` valid (not expired, not rate-limited)? Test with `uv run python -c "from langsmith import Client; print(Client().list_projects())"`. |
| `cost_usd = 0.0` on a blocking run | The code path must go through `invoke_with_observability`. If you bypass it and call `graph.invoke` directly, the cost callback is never attached. |
| `cost_usd = 0.0` on a streamed run | The `astream_events` loop must sit **inside** `with get_usage_metadata_callback()`. If the `with` exits before the `async for` completes, the callback sees nothing. |
| `latency_ms` missing on the root | Both paths must carry it: `invoke_with_observability` measures for blocking, `enrich_run_from_stream` attaches it for streaming. If neither fires, the field won't appear. |
| Run landed in the wrong project | `project_scope(env)` reads `config["metadata"]["env"]`. If `build_run_config(env=...)` was called with a stale value, the project will be wrong. Verify the entrypoint in `app/api/routes/chat.py:_run_config`. |
| Per-node metadata missing | The node needs both `@traceable(...)` and an `attach_span_metadata({...})` call inside the function body. The decorator alone creates the span; the helper populates it. |
| Token count present, `cost_usd = 0.0` | The model isn't in `PRICING_PER_1M` in `app/obs/pricing.py`. Add it — unknown models cost 0 and will silently under-report. |
| LangSmith UI shows the trace but misses the final cost/latency patch | `_update_run` is best-effort. If the LangSmith API is flaky that request, the patch is dropped. The run still renders; the patch-only fields just won't appear. Re-running usually fixes it. |

---

## 8. Common Confusions

| Confusion | Clarification |
|---|---|
| "Why does the root run only show cost/latency *after* the graph finishes?" | Because we patch it post-hoc via `_update_run`. The root span is created when the request starts (so it shows up in the UI immediately), but we can't know total cost or E2E latency until the graph is done. That's why those fields appear a moment later than the rest. |
| "Why is `env` both in metadata and in tags?" | Metadata is for detailed drill-down (full values, searchable). Tags are for fast filtering in the UI (indexed, faceted). Most human workflows use tags; programmatic queries read metadata. |
| "If LangSmith is down, does the graph still work?" | Yes. Every tracing/enrichment call in `app/obs/tracing.py` is best-effort (wrapped in try/except). You lose observability, not functionality. This is a deliberate choice — observability should never be in the critical path. |
| "What's the difference between `faithfulness` and `groundedness`?" | Same concept (does the answer stick to the context), different implementations. `groundedness_evaluator` is our in-repo LLM-judge. `faithfulness` is Ragas's version — currently computed offline, not yet as a LangSmith evaluator. Phase 4 of `eval-tracing-plan.md` renames them to `groundedness_llm_judge` and `faithfulness_ragas` to make the distinction obvious. |
| "Why can't I see per-node latency on the root?" | Each span's duration is on the span itself, not copied up. To compare, open the tree view — LangSmith shows span durations visually as a flamegraph. |

---

## 9. Further Reading (from your own shelf)

- **SRE book, ch. "Monitoring Distributed Systems"** — the four golden signals. Our `latency_ms` + `cost_usd` + evaluator-fail-rate are the LLM equivalents.
- **SRE book, ch. "Effective Troubleshooting"** — the hypothesis-test-refine loop. Maps exactly onto the 5-minute debug workflow in §2.
- **DDIA, ch. 10 "Batch Processing"** — mental model for golden-dataset eval as a batch job.
- **LLMOps book** — chapters on observability and evaluation; the groundedness/faithfulness distinction we use here is lifted from the Ragas foundations surveyed there.
- **LLM Security book** — prompt injection via retrieved context; the groundedness judge doubles as a weak detection signal for "did the model follow an instruction planted in a retrieved doc."

---

## 10. What's Next

- Phase 3 / 4 of `docs/tracking/eval-tracing-plan.md`: add `latency_ms`, `classification_accuracy`, `non_technical_clarity` to the per-run report and expose them as LangSmith evaluators.
- Phase 5: wire the online evaluator + monitor as described in §6.
- When production traffic exists, this doc's §3 filters will be updated with the actual thresholds we see in real traffic (current numbers are educated guesses).
