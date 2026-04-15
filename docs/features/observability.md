# Observability — Move Mind AI

> Status: initial draft (Week 2 Day 5). Dogfooding happens over the next several days as real traces accumulate.
> Sprint reference: `docs/tracking/week2-plan.md`.

This document is the runbook for everyone who has to answer the question **"why did the assistant give that answer?"** — whether debugging a single bad response or watching quality drift in aggregate.

---

## 1. Trace Anatomy

Every `/api/v1/chat` request (and every eval run) emits one LangSmith run tree. The tree mirrors the graph in `app/graphs/agent.py`:

```
run: chat(question="...")                     [root]
├── classify_question                          [llm]
│   └── gpt-4o-mini
├── (optional) rewrite_question                [llm]
│   └── gpt-4o-mini
├── resolve_context                            [chain]
├── retrieve_docs                              [retriever]
│   └── vectorstore.similarity (+ BM25)
├── rerank_docs                                [retriever]
│   └── FlashRank
├── generate_answer                            [chain]
│   └── gpt-4o  OR  o3 (if deep-reasoning)
└── classify_issue                             [llm]
    └── gpt-4o-mini
```

The root run carries the aggregate metadata written by `app/obs/tracing.py`:

| Field | Where it comes from |
|---|---|
| `env` | `build_run_config(env=...)` — `dev`, `eval`, `prod` |
| `explanation_mode` | `manager` (default) or `developer` |
| `session_id` / `thread_id` | LangGraph thread — same across turns in a conversation |
| `question_preview` | First 200 chars of the user question |
| `cid` | `active_customer_id` extracted by `resolve_context` |
| `query_type` | `retrieve` or `rewrite` (output of `classify_question`) |
| `issue_type` | `bug` / `business_condition` / `unknown` |
| `issue_confidence` | Classifier confidence 0–1 |
| `cost_usd` / `total_input_tokens` / `total_output_tokens` | Aggregated via `get_usage_metadata_callback` + `app/obs/pricing.py` |
| `per_model` | Per-model token + cost breakdown |

Nodes attach their own structured events:

| Node | Attributes |
|---|---|
| `retrieve_docs` | `k_summary`, `k_event`, `num_returned`, `analysis_mode` |
| `rerank_docs` | `num_input`, `num_kept`, `cutoff` (plus `bypass_reason` when API-timeline mode bypasses rerank) |
| `classify_issue` | `issue_type`, `issue_confidence` |

Tags let you filter in the LangSmith UI: `env:dev`, `mode:manager`, `cid:7093495`, `issue:bug`.

---

## 2. How to Debug a Bad Answer (target: < 5 minutes)

1. **Find the run.** LangSmith → `move-mind-dev` → filter by `cid:<cid>` or search on `question_preview`. Open the root run.
2. **Scan cost and latency at the root.** If latency > ~10s or cost > ~$0.05, flag it — most answers should cost 1–3¢.
3. **Walk the tree top-down.**
   - `classify_question`: correct routing? `rewrite` only when the question is a vague follow-up.
   - `resolve_context`: did `active_customer_id` / `active_page_path` get set? If not, the rest is running blind.
   - `retrieve_docs`: check `num_returned`. `0` → retrieval miss.
   - `rerank_docs`: check `num_kept`. If `num_kept < 2`, the answer had thin evidence.
   - `generate_answer`: open the LLM span, read the prompt + completion. This is where hallucinations show up.
   - `classify_issue`: if `issue_type=unknown` with high-information context, the classifier prompt likely needs tuning.
4. **Cross-check the evaluator scores** (experiment runs only) — keyword_hit + jargon_leak + groundedness give three different angles on the same answer.

### Common failure fingerprints

| Symptom | Likely span |
|---|---|
| Answer is confidently wrong | `generate_answer` — groundedness low, faithfulness low |
| Answer is "I couldn't find anything" | `retrieve_docs` returned 0, or `resolve_context` missed the CID |
| Answer mixes two customers | `resolve_context` — check `active_customer_id` between turns |
| Latency tail | Read `rerank_docs` duration + LLM span in `generate_answer` |
| Cost spike | Check `per_model` — `o3` triggered for a question that didn't need it |

---

## 3. Reading the Dashboard

Default filters to save in LangSmith:

- **Bug trace** — `tags: env:dev, issue:bug`
- **Poor retrieval** — `metadata: retrieve_docs.num_returned = 0`
- **Thin evidence** — `metadata: rerank_docs.num_kept < 2`
- **o3 escalation** — any LLM span with model `o3`
- **High cost** — `metadata: cost_usd > 0.05`

Pair those with the experiment UI (see §5) to spot which runs tripped an evaluator.

---

## 4. Running Eval Locally

```bash
# 1. One-time: upload the golden dataset to LangSmith (idempotent)
uv run python scripts/upload_dataset.py

# 2. Run the full eval (Ragas + custom metrics + JSON report)
bash scripts/run_eval.sh

# 3. Only check the regression gate (needs latest_results.json)
bash scripts/check_regression.sh

# 4. Skip LangSmith (offline-only)
bash scripts/run_eval.sh --skip-langsmith
```

`scripts/run_eval.sh` writes `data/eval/latest_results.json`, diffs it against `data/eval/baseline_results.json`, and — if `LANGCHAIN_API_KEY` is set — also launches a LangSmith experiment on the `golden-v1` dataset with the three evaluators from `app/eval/langsmith_evaluators.py`.

---

## 5. Interpreting the Regression Gate

`app/eval/diff.py` compares the overall metric block in `latest_results.json` against `baseline_results.json`.

| Metric | Direction | Max drift |
|---|---|---|
| `faithfulness` | higher is better | 0.03 |
| `answer_relevancy` | higher is better | 0.03 |
| `keyword_hit_rate` | higher is better | 0.03 |
| `jargon_leak_rate` | **lower** is better | 0.02 |

The gate reports one of three states per metric: `OK`, `WARN` (moved in the bad direction but within budget), `FAIL` (exceeded budget).

**Updating the baseline is an explicit, committed action:**

```bash
uv run python -m app.eval.diff \
  --current data/eval/latest_results.json \
  --update-baseline
```

The commit message must justify the move — e.g., "answer prompt rewrite improved faithfulness 0.64 → 0.71, baseline refreshed". A baseline bump without justification is a silent regression the next time.

---

## 6. Online Evaluation (pending)

Once real production traffic exists (see `docs/tracking/week2-plan.md` Day 5), configure a LangSmith online evaluator to sample ~10% of `move-mind-prod` runs and run the groundedness judge continuously. A LangSmith Monitor should alert if rolling 24h groundedness drops below 0.70. Both are no-ops today because we don't yet have production traffic volume.

---

## 7. Troubleshooting Observability Itself

| Problem | Check |
|---|---|
| No traces appearing | `LANGCHAIN_TRACING_V2=true` in `.env`? `LANGCHAIN_API_KEY` valid? |
| Cost is `0.0` on every run | `get_usage_metadata_callback` not attached — is the code path going through `invoke_with_observability`? |
| Metadata missing on streaming endpoints | `enrich_run_from_state` isn't being called at the end of the SSE generator |
| Model not in `PRICING_PER_1M` | Add it to `app/obs/pricing.py` — unknown models cost 0 which will silently under-report |
