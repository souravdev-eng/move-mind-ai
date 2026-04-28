# Eval Pipeline — A Walkthrough

> **Teaching doc.** This explains *what* we measure on the assistant, *why* those metrics (and not others), and *how* the offline + online pieces fit together into a regression gate. Covers the current state accurately — planned metrics are marked **(planned)** so you don't reach for something that isn't there yet.
>
> Read after [`observability.md`](./observability.md) (which covers debugging individual answers) and [`langsmith-integration.md`](./langsmith-integration.md) (which covers how traces get captured).

---

## 0. Why Eval Exists (and Why It's Different for LLMs)

Traditional software testing works because behavior is deterministic: same input → same output. You assert the output; pass or fail.

LLMs break that assumption in three ways:

1. **Non-determinism.** Even at `temperature=0`, two runs can differ (sampling, caching, provider-side variability).
2. **No "correct" output — a range of acceptable ones.** "Summarise customer 7093495's journey" has many valid phrasings. Exact-match is useless.
3. **Failures are semantic, not syntactic.** A plausible-sounding wrong answer passes every structural check.

So we can't write `assertEqual(answer, expected)`. We need measurement, not assertion — multiple imperfect metrics that, taken together, tell us whether quality went up, down, or sideways. That's what this pipeline does.

### The mental model — one paragraph

We maintain a **golden dataset** of 27 representative questions with expected signals (keywords, forbidden jargon, reference answers). For every experiment, we run each question through the live graph, compute four metrics (two structural, two LLM-judged) per answer, and aggregate. A second script compares today's aggregates against a locked baseline and fails the build if any metric drifted too far in the bad direction. The baseline itself is a committed JSON file — bumping it requires an explicit commit with justification. That's the whole loop.

---

## 1. The Golden Dataset (`data/eval/golden_dataset.json`)

The dataset is the contract between us and the assistant. Every entry says: *"when asked this, the answer should look like this."*

### Schema (current, as of the Week 2 snapshot)

```json
{
  "id": "CID-001",                     // stable identifier, used in logs and LangSmith tags
  "category": "cid_lookup",            // see category table below
  "question": "What happened to CID 7093495?",
  "expected_keywords": [               // fractions of these must appear in the answer
    "returning customer",
    "booking",
    "78",
    "successful",
    "quote"
  ],
  "expected_not_contains": [           // none of these should appear (jargon blocklist)
    "decision_result",
    "graphql_request",
    "gql_",
    "chunk_type",
    "step_order"
  ],
  "ground_truth": "Customer 7093495 was a returning customer who ...",
  "notes": "Should describe a full successful journey ..."
}
```

Multi-turn entries add `prior_question`, `turn`, and optionally `depends_on`, so the runner can prime a session with the prior turn before asking the follow-up (see `app/eval/runner.py:60`).

### Categories (27 total today)

| Category | Count | What it tests |
|---|---|---|
| `cid_lookup` | 6 | Direct questions about one customer. Checks context resolution + retrieval on the right CID. |
| `root_cause` | 6 | "Why did this fail?" questions. Stresses reasoning over retrieved log chunks. |
| `business_condition` | 5 | Questions about journey outcomes ("was this a successful move?"). Tests the classifier/rewriter boundary. |
| `api_timeline` | 5 | Timeline queries that bypass rerank. Tests the `analysis_mode="api_timeline_summary"` path. |
| `multi_turn` | 5 | Follow-up questions. Tests session memory and `query_type="rewrite"` routing. |

### Why this shape?

A few deliberate choices:

- **Keyword check (must contain).** Cheap, deterministic, catches "did the model mention the key facts?" It's a low bar — but reliably low.
- **Jargon blocklist (must not contain).** Our audience is *non-technical managers*; leaking raw log field names (`step_order`, `gql_…`) is a product failure even if the answer is factually right. This catches that specifically.
- **`ground_truth` reference.** Required by some Ragas metrics (like `context_recall`) and useful for human review. Not used by the current keyword-based metrics, but worth keeping since it unblocks future metrics without a dataset migration.
- **Category field.** Lets us aggregate performance per failure mode, not just overall. A 0.90 overall score can hide a 0.40 on `multi_turn` — the per-category breakdown catches that.

### Why keep the dataset small (27)?

Three reasons:

1. **Hand-curated quality.** Every question was chosen to exercise a specific pathway. 27 high-quality > 270 generic.
2. **Iteration speed.** Full eval runs in ~5 min. If we had 500 questions + Ragas judgements, we'd run eval once a week, not on every prompt change.
3. **Cost.** Each question = ~4 LLM calls in the graph + 3 LLM-judge calls in evaluators. At 27 questions × gpt-4o pricing, one full eval is under $1. At 500 questions it stops being free to run.

**When to grow it.** When we see a real-world failure mode the dataset doesn't cover, add that specific question — don't grow by generation. The golden set should always be *representative of what breaks*, not of "what users might ask in general" (LangSmith already captures the latter in production traces).

---

## 2. The Four Metrics — what each measures and why it exists

### 2.1 `keyword_hit_rate` — did the answer mention the key facts?

**Computation.** Case-insensitive substring match: `hits / len(expected_keywords)`. See `app/eval/metrics.py:16`.

**Target.** `≥ 0.80`.

**Why this metric exists.** It's the cheapest possible sanity check: "did the model's answer mention the things a good answer must mention?" It won't catch hallucinations (plenty of wrong answers contain the right keywords), but it will catch regressions where the model *stops* mentioning them — often a sign that retrieval went wrong or the prompt stopped emphasising them.

**Why not a fancier matcher (embedding similarity)?** Because the keywords are business-level phrases we *want* to see literally ("78 steps", "booking page"). Semantic similarity would score "about 80 actions" as similar to "78 steps" — but we specifically want the exact number. Determinism beats cleverness here.

**What low scores mean.** Either the assistant is paraphrasing away from the canonical vocabulary (may or may not be a problem), or it's missing a key fact (definitely a problem). Open the specific failed question in LangSmith and read the answer to tell them apart.

### 2.2 `jargon_leak_rate` — did the answer speak manager-speak?

**Computation.** Same mechanism as `keyword_hit_rate`, but **lower is better**: `leaks / len(expected_not_contains)`. See `app/eval/metrics.py:30`.

**Target.** `< 0.10`.

**Why this metric exists.** The product goal per the memory is "reduce dev investigation effort from 50% to 10%". Managers won't read answers full of raw log field names. A factually correct answer that includes `decision_result` or `graphql_request` has *failed the product* even though it would pass a correctness check. So we measure jargon leakage explicitly and gate on it.

**Why substring match, not LLM-judge?** Because the blocklist is a *known set of forbidden tokens*, not a vibe. "Does the answer mention `graphql_request`" is yes/no; there's nothing to judge. Use the cheapest tool that answers the question.

**What high scores mean.** The prompt template or the retrieved chunks are bleeding raw log field names into the completion. The fix is usually in `app/prompts/templates.py` (explicit instruction to rephrase in plain English) or, for repeated offenders, a post-hoc scrubber.

### 2.3 `faithfulness` — does every claim have context support? (Ragas)

**Computation.** Ragas's `Faithfulness` metric. It breaks the answer into atomic claims, then for each claim asks an LLM judge "is this claim entailed by the retrieved context?" Score = fraction entailed. See `app/eval/metrics.py:64`.

**Target.** `≥ 0.80`.

**Why this metric exists.** This is the single most important quality signal in a RAG system. Hallucination is the primary failure mode, and it's invisible to keyword checks. Faithfulness explicitly measures "are you making things up?"

**Why Ragas specifically?** It's the de-facto library for RAG evaluation; its faithfulness implementation is peer-reviewed and maintained. We'd build something equivalent; Ragas saves us that build.

**Why run Ragas offline, not as a LangSmith evaluator (today)?** Historical. The initial eval module used Ragas standalone; we've since added LangSmith evaluators for the structural metrics. Phase 4 of `eval-tracing-plan.md` adds a `faithfulness_ragas` LangSmith evaluator so the score shows up natively in the experiment UI. Today: Ragas runs in `compute_ragas_metrics`, scores go into `latest_results.json`, and you read them from the human-readable report printed by `app/eval/report.py` or the diff.

**Failure mode to know about.** Ragas can fail (API error, token limits, parse errors) — we catch, log, and set scores to `None` rather than crashing. See `app/eval/metrics.py:133`. A run where `faithfulness` is `None` isn't a zero — it's "we don't know." The diff gate will `SKIP` rather than `FAIL` in that case. Don't misread a gap as a drop.

### 2.4 `answer_relevancy` — does the answer address the question? (Ragas)

**Computation.** Ragas's `AnswerRelevancy`. Given the answer, it generates N plausible questions that would produce such an answer, then measures cosine similarity between each generated question and the original. High score = the answer's "shape" matches what the user actually asked. See `app/eval/metrics.py:64`.

**Target.** `≥ 0.70`.

**Why this metric exists.** Faithfulness catches "is the answer factually supported?" but not "is it *addressing the question*?" An answer can be 100% faithful to retrieved context and still be tangential ("You asked about customer X; here's the company's refund policy" — every sentence true, every sentence irrelevant). Answer relevancy catches that class of failure.

**Why 0.70, not 0.80?** The metric is inherently noisier than faithfulness (it depends on the generation of alternative questions + embedding similarity). A 0.70 target is calibrated from early runs. Phase 3 of `eval-tracing-plan.md` flags a target bump to 0.75 once we have enough data to pick a defensible number.

### Why these four and not more (yet)?

Marginal cost vs marginal signal. Every metric you add is another piece of code to maintain, another target to tune, and (for LLM-judged ones) another LLM call per question. These four cover three different failure modes:

| Failure mode | Primary metric that catches it |
|---|---|
| Missing a key fact | `keyword_hit_rate` |
| Speaks in jargon | `jargon_leak_rate` |
| Hallucinates | `faithfulness` |
| Tangential / off-topic | `answer_relevancy` |

More metrics are planned (`context_precision`, `context_recall`, `non_technical_clarity`, `classification_accuracy`, `latency_ms`), but they each have a specific role not already covered:

- `context_precision` / `context_recall` — evaluate *retrieval* separately from generation.
- `classification_accuracy` — does `classify_question` route correctly?
- `non_technical_clarity` — LLM-judged readability for non-technical managers.
- `latency_ms` — treat the E2E time like any other SLI.

See `docs/tracking/eval-tracing-plan.md` Phase 3 for the rollout order.

---

## 3. The Pipeline — what happens when you run `bash scripts/run_eval.sh`

```
┌────────────────────────────────────────────────────────────────────┐
│ 1. scripts/run_eval.sh                                             │
│                                                                    │
│    ▶ uv run python -m app.eval.cli --output data/eval/latest_...   │
│       │                                                            │
│       ▼                                                            │
│    ┌──────────────────────────────────────────────────┐            │
│    │ app/eval/runner.py :: run_eval(dataset_path)     │            │
│    │   for each question:                             │            │
│    │     build_run_config(env="eval", ...)            │            │
│    │     invoke_with_observability(graph, ...)        │            │
│    │   returns list[dict] with answer + contexts      │            │
│    └──────────────────────────────────────────────────┘            │
│       │                                                            │
│       ▼                                                            │
│    ┌──────────────────────────────────────────────────┐            │
│    │ app/eval/metrics.py :: compute_custom_metrics    │            │
│    │   adds keyword_hit_rate, jargon_leak_rate        │            │
│    │   adds missed_keywords, leaked_jargon (for UI)   │            │
│    └──────────────────────────────────────────────────┘            │
│       │                                                            │
│       ▼                                                            │
│    ┌──────────────────────────────────────────────────┐            │
│    │ app/eval/metrics.py :: compute_ragas_metrics     │            │
│    │   runs Ragas Faithfulness + AnswerRelevancy      │            │
│    │   via gpt-4o (smart model — mini hits limits)    │            │
│    └──────────────────────────────────────────────────┘            │
│       │                                                            │
│       ▼                                                            │
│    ┌──────────────────────────────────────────────────┐            │
│    │ app/eval/report.py :: generate_report            │            │
│    │   aggregates per-category + overall averages     │            │
│    │   writes data/eval/latest_results.json           │            │
│    │   prints a human-readable summary table          │            │
│    └──────────────────────────────────────────────────┘            │
│                                                                    │
│ 2. ▶ uv run python -m app.eval.diff --current latest --baseline..  │
│    ┌──────────────────────────────────────────────────┐            │
│    │ app/eval/diff.py                                 │            │
│    │   compares overall metrics to baseline           │            │
│    │   classifies each: OK / WARN / FAIL              │            │
│    │   exit 1 if any FAIL                             │            │
│    └──────────────────────────────────────────────────┘            │
│                                                                    │
│ 3. ▶ uv run python scripts/run_langsmith_eval.py     (if key set)  │
│    ┌──────────────────────────────────────────────────┐            │
│    │ uploads experiment to LangSmith                  │            │
│    │ runs ALL_EVALUATORS in the experiment UI         │            │
│    │ experiment_prefix includes git short SHA         │            │
│    └──────────────────────────────────────────────────┘            │
└────────────────────────────────────────────────────────────────────┘
```

Every arrow is a function call you can open and read. No dark magic.

### Design notes on each stage

**The runner uses the *real* graph.** `run_eval` calls `invoke_with_observability` with `env="eval"` — the exact same code path production uses, routed to the eval LangSmith project. We deliberately do not mock anything. A mocked eval catches code-shape regressions but misses the interesting ones (retrieval misses, reranker drift, model misbehaviour on weird prompts). The trade-off is cost and latency; we pay both willingly.

**Multi-turn priming (`app/eval/runner.py:61`).** For `category == "multi_turn"` entries with a `prior_question`, we invoke that question first in the same `session_id`. This makes the follow-up run against the real session state, the way a manager would ask it. Without priming, the multi-turn questions would be evaluated as standalone — which misses the whole point of testing session memory.

**Why gpt-4o for Ragas, not gpt-4o-mini?** Ragas sends the *entire* retrieved context to the judge. Our log contexts can be 3–8k tokens. `gpt-4o-mini` often hits token limits and returns truncated output, which Ragas parses as zero. `gpt-4o` handles the context reliably. Cost is ~$0.02 per run — worth it for reliable scores. See `app/eval/metrics.py:83`.

**Why results are per-question + per-category + overall?** Because you want three different questions from the same data:
- Per-question: "which specific answer regressed?"
- Per-category: "did a whole class of questions get worse?"
- Overall: "is the product getting better?"

The aggregation happens once in `report.py` and all three views come from the same pass.

---

## 4. The Regression Gate (`app/eval/diff.py`)

### What it does

Compares `data/eval/latest_results.json` (this run) against `data/eval/baseline_results.json` (the locked reference). For each of the four metrics, it computes `delta = current - baseline` and classifies:

- **OK** — metric moved in the good direction, or stayed within budget in the bad direction with delta ≤ 0.
- **WARN** — metric moved in the bad direction but stayed within `max_drift`. Worth a look, not blocking.
- **FAIL** — metric exceeded `max_drift` in the bad direction. Exit code 1 — blocks the merge.
- **SKIP** — metric is `None` on one side (usually Ragas failed). Not a regression, just no comparison possible.

### Drift budgets

```python
GATE_CONFIG = {
    "faithfulness":      {"max_drift": 0.03, "lower_is_better": False},
    "answer_relevancy":  {"max_drift": 0.03, "lower_is_better": False},
    "keyword_hit_rate":  {"max_drift": 0.03, "lower_is_better": False},
    "jargon_leak_rate":  {"max_drift": 0.02, "lower_is_better": True},
}
```

### Why drift budgets, not strict `current >= baseline`?

LLM metrics are noisy. Even with `temperature=0`, two runs of the same dataset can differ by 0.01–0.02 on Ragas scores. A strict "must not decrease" gate would page on noise, teaching everyone to ignore the gate — which defeats the purpose.

Drift budgets separate **signal from noise**:
- Within budget = within expected variance. Don't alert.
- Outside budget = probably a real change. Alert.

This is the exact same logic as a latency SLO: you don't page on every millisecond of variance, you page on sustained deviation from the objective.

### Why `jargon_leak_rate` has a tighter budget (0.02, not 0.03)

Jargon leakage is unidirectional: it only leaks because the prompt or the retrieval is bleeding field names. The variance from *noise* is near zero — so a 0.03 budget would tolerate actual regressions. A 0.02 budget is tight enough that any real leakage trips the gate. The other three metrics are LLM-judged and noisier.

### Updating the baseline — an explicit, committed action

```bash
# Option A — via the standalone diff script
uv run python -m app.eval.diff \
  --current data/eval/latest_results.json \
  --update-baseline

# Option B — via the pipeline script
bash scripts/run_eval.sh --update-baseline
```

### Why the baseline is a file in the repo, not a database row?

Three reasons:

1. **Git history is the audit trail.** Every baseline bump is a commit. The commit message explains *why* the baseline moved. Six months from now, the blame log tells you "this is the version where the prompt rewrite improved faithfulness from 0.64 to 0.71."
2. **Reproducible.** Anyone can check out an old commit and run eval against that commit's baseline. Nothing external required.
3. **No service to operate.** A database of baselines sounds slick until you realise it needs backups, migrations, and an API.

**The rule:** a baseline bump without justification in the commit message is a silent regression waiting to compound. Always explain the move.

---

## 5. LangSmith Experiments vs Offline Eval — two windows on the same run

The script runs both:

| | Offline eval (`app/eval/cli.py` + `diff.py`) | LangSmith experiment (`scripts/run_langsmith_eval.py`) |
|---|---|---|
| **Output** | `latest_results.json` + summary table + exit code | Rows in LangSmith's Experiments UI + per-example traces |
| **Metrics** | `keyword_hit_rate`, `jargon_leak_rate`, `faithfulness`, `answer_relevancy` | `keyword_hit_rate`, `jargon_leak_rate`, `groundedness` (LLM-judge) |
| **Regression detection** | Yes — automated diff gate | Manual — compare experiments visually |
| **Drill-down** | Read JSON, grep for IDs | Click into any example, see the full trace tree |
| **Cost** | ~$1 per run (Ragas dominates) | ~$0.30 per run (groundedness judge + graph runs already counted in offline) |

### Why both?

They serve different roles:

- **Offline eval** is the *gate* — it fails the build. Automated, deterministic, CI-friendly.
- **LangSmith experiment** is the *inspection surface* — it lets a human click through the run and see exactly what happened for each example. Great for "faithfulness dropped; why?"

Neither replaces the other. Running both in the same `run_eval.sh` execution means they evaluate the same graph invocation, so scores are directly comparable.

**Why `groundedness` (LangSmith) and `faithfulness` (offline) are not deduplicated.** They measure the same concept but differ in implementation:

- `groundedness` — our in-repo LLM-judge (`app/eval/langsmith_evaluators.py:85`). Simpler prompt, `gpt-4o-mini`, one call per answer.
- `faithfulness` — Ragas's atomic-claim decomposition. More rigorous, `gpt-4o`, several calls per answer.

Seeing both lets us cross-check. If they disagree, something is suspicious about the answer (usually: it has a mix of well-supported and borderline claims). Phase 4 of `eval-tracing-plan.md` renames them to `groundedness_llm_judge` + `faithfulness_ragas` for clarity.

---

## 6. Runbook — Use It Yourself

### Day-to-day: run the full pipeline

```bash
bash scripts/run_eval.sh
```

Reads the golden dataset, runs the graph, computes metrics, diffs vs baseline, fires a LangSmith experiment. Takes ~5–8 min. Exit code 1 if anything regressed.

### Iteration: skip Ragas (faster)

```bash
uv run python -m app.eval.cli --skip-ragas
```

Runs the graph + custom metrics only. ~2 min. Useful when you're iterating on keyword/jargon lists.

### Diagnosis: diff without running

```bash
uv run python -m app.eval.diff \
  --current data/eval/latest_results.json \
  --baseline data/eval/baseline_results.json
```

Rerun the diff against existing files. Zero-cost.

### After an intentional improvement: bump the baseline

```bash
bash scripts/run_eval.sh --update-baseline
git diff data/eval/baseline_results.json   # confirm the numbers you expected
git commit -am "eval: bump baseline — prompt rewrite improved faithfulness 0.64 → 0.71"
```

Always commit with a message that names *what changed* and *what metric moved*. Future-you will thank present-you.

### After a regression: investigate in LangSmith

1. Note which metric failed in the diff table.
2. Open LangSmith → `move-mind-eval` → Experiments tab.
3. Find the experiment matching the git SHA from this run (prefix: `golden-v1-YYYYMMDD-HHMMSS-<sha>`).
4. Sort by the failing metric's column. Click into the worst example.
5. You're now in a trace. Use the debug recipe in [`observability.md` §5](./observability.md#5-debug-runbook--full-recipe).

---

## 7. Common Confusions

| Confusion | Clarification |
|---|---|
| "Why is `jargon_leak_rate` lower-is-better?" | The metric is *rate of forbidden terms present*. More jargon leaked = higher number = worse answer. `lower_is_better: True` in `GATE_CONFIG` flips which direction counts as "bad" for the drift calculation. |
| "Why do some runs show `faithfulness = None`?" | Ragas failed for that run (API error, parse error, token limit). Treated as "unknown", not "zero" — the gate `SKIP`s the metric rather than failing it. Rerun when the underlying issue is fixed. |
| "Why is the golden dataset so small?" | Deliberate. Hand-curated questions covering distinct failure modes beat 10× generated questions. See §1. |
| "Can I add a question I just saw fail in production?" | Yes — that's exactly the right workflow. Add it to `golden_dataset.json`, rerun `bash scripts/run_eval.sh --update-baseline`, commit both files with a message tying the new question to the production incident. |
| "Why not Pytest?" | Pytest wants pass/fail per test. Our metrics are continuous, noisy, and aggregate across 27 questions. We borrowed the *idea* of a gate (fail the build on regression) but built it around diff-against-baseline instead of per-test assertions. |
| "Why doesn't the offline eval use the same evaluators as the LangSmith experiment?" | Historical — the offline path was built first around Ragas, the LangSmith path around the structural metrics + an in-repo groundedness judge. Phase 4 converges them. |
| "The diff says WARN but all metrics passed `passes_threshold` in the report. What gives?" | Different comparisons. `passes_threshold` compares against absolute targets (`faithfulness ≥ 0.80`). The diff compares against the *committed baseline* + drift budget. A run can pass absolute thresholds and still warn if it dropped vs. the prior committed run. |

---

## 8. Further Reading (from your own shelf)

- **LLMOps book, evaluation chapters** — the RAG-specific metric family (faithfulness, answer relevancy, context precision/recall) comes directly from the Ragas foundations surveyed there.
- **DDIA, ch. 10 "Batch Processing"** — mental model for eval-as-batch-job over a fixed dataset. Our pipeline is a tiny batch job.
- **SRE book, chapters on SLOs and error budgets** — the drift-budget philosophy in §4 is the SLO/error-budget idea ported from latency to model quality.
- **GenAI Design Patterns** — the "Eval-Driven Development" pattern is exactly this loop: ship behind a committed baseline + regression gate.
- **Fundamentals of Data Engineering** — schema versioning discussion applies to the golden dataset; when you change its shape, think about forward-compat.

---

## 9. What's Next (from `docs/tracking/eval-tracing-plan.md`)

Phase 3 / 4 adds five metrics on top of today's four:

| Metric | Kind | Role |
|---|---|---|
| `context_precision` | Ragas | Of the retrieved docs, how many were actually relevant to answering the question? |
| `context_recall` | Ragas | Of the docs needed to answer, how many were retrieved? Requires `ground_truth`. |
| `classification_accuracy` | Custom | Did `classify_question` route correctly (retrieve vs rewrite)? Needs `expected_query_type` in the dataset. |
| `non_technical_clarity` | LLM-judge | Is the answer readable by a non-technical manager? Listed in the sprint doc; not built yet. |
| `latency_ms` | Custom | E2E latency per question. Already captured on root runs; Phase 3 pulls it into the report. |

Phase 4 promotes `faithfulness` and `answer_relevancy` from offline-only to LangSmith evaluators, so all scores appear in one place.

Phase 5 archives `/data/eval_results.json` (stale March-2026 AMS Admin Tool run, different domain) and sets up a LangSmith **online evaluator** that samples 10% of production runs and applies `groundedness_llm_judge` continuously — the missing piece between offline batch eval (what we know) and real user traffic (what we don't).

Once each phase lands, this doc's metric tables get a row appended, and `eval-tracing-plan.md` gets a `Status` column tick.
