# Eval & Observability: LangSmith Tracing + Metrics Capture Plan

Full-stack plan to complete LangSmith tracing coverage, close eval metric gaps, and document every implementation in `docs/features/`.

> **Status (2026-04-16):** Phases 1 + 2 complete. TR-01 through TR-08 closed; see "Status" column below and `docs/features/langsmith-integration.md`. Phases 3–5 (EV-01..EV-10, baseline reset, online eval) are the next chunk.

---

## Part 1 — Code Audit Findings

### A. Tracing Gaps (`app/obs/`)

| ID | File | Gap | Severity | Status |
|----|------|-----|----------|--------|
| TR-01 | `app/graphs/nodes/rewrite_question.py` | No `@traceable` decorator — span not visible in LangSmith | High | ✅ Done (already present at line 11) |
| TR-02 | `app/graphs/nodes/resolve_context.py` | No `@traceable` — `active_customer_id` extraction invisible in trace tree | High | ✅ Done (line 55) |
| TR-03 | `app/graphs/nodes/retrieve_docs.py` | No `@traceable` + `attach_span_metadata` not called — `k_summary`, `k_event`, `num_returned` only documented in `observability.md` but not actually written to spans | High | ✅ Done (lines 14, 29–36) |
| TR-04 | `app/graphs/nodes/rerank_docs.py` | No `@traceable` — rerank span not visible; `num_input`, `num_kept` not attached via `attach_span_metadata` | High | ✅ Done (lines 14, 23–50) |
| TR-05 | `app/obs/tracing.py` → `invoke_with_observability` | No `latency_ms` measured or attached to root run metadata — E2E timing is invisible | High | ✅ Done (measured via `time.perf_counter()`; attached on blocking + streaming paths) |
| TR-06 | `app/api/routes/chat.py` (streaming path) | `enrich_run_from_state` pushes cid/issue_type but NOT token/cost (cost requires `get_usage_metadata_callback` context manager, which only wraps `invoke_with_observability`) — streaming runs show $0 cost | Medium | ✅ Done (`astream_events` loop wrapped in callback; `enrich_run_from_stream` posts cost + latency) |
| TR-07 | `app/config.py` | `LANGCHAIN_PROJECT` is a single value `move-mind-ai` regardless of env — dev/eval/prod traces all mixed in one project | Medium | ✅ Done (`LANGCHAIN_PROJECT_{DEV,EVAL,PROD}` + `project_scope(env)`) |
| TR-08 | `scripts/run_langsmith_eval.py` | Experiment prefix is date-based only; no git commit hash — can't correlate experiment to exact code version | Low | ✅ Done (`golden-v1-<ts>-<git_short_sha>`) |

---

### B. Eval Metric Gaps (`app/eval/`)

| ID | File | Gap | Severity |
|----|------|-----|----------|
| EV-01 | `app/eval/metrics.py` | `context_precision` and `context_recall` listed as planned metrics in `docs/tracking/eval-sprint.md` but never implemented — 2 of 7 sprint metrics missing | High |
| EV-02 | `app/eval/metrics.py` | No `latency_ms` metric — E2E timing not tracked per question in eval results | High |
| EV-03 | `app/eval/metrics.py` | No `classification_accuracy` metric — `classify_question` routing (retrieve vs rewrite) correctness never measured | Medium |
| EV-04 | `app/eval/metrics.py` | No LLM-as-judge "non-technical clarity" scorer — listed as `Non-Technical Clarity > 0.75` in sprint doc, not built | Medium |
| EV-05 | `app/eval/metrics.py` | `answer_relevancy` threshold is `0.70` but sprint doc specifies `0.75` — mismatch between target and gate | Low |
| EV-06 | `app/eval/langsmith_evaluators.py` | Ragas `faithfulness` and `answer_relevancy` scores are computed locally but never pushed as LangSmith evaluators — only `keyword_hit`, `jargon_leak`, `groundedness` land in experiment UI | High |
| EV-07 | `app/eval/langsmith_evaluators.py` | `groundedness_evaluator` (LLM-as-judge) and Ragas `faithfulness` measure the same concept with different implementations — no explicit differentiation or consolidation | Low |
| EV-08 | `data/golden_dataset.json` | Most entries have `expected_keywords` + `expected_not_contains` only; `context_recall` requires reference `ground_truth` answers — some entries have `ground_truth` but schema is inconsistent | Medium |
| EV-09 | `data/eval_results.json` | Active file is from a March 2026 AMS Admin Tool run (different domain, `gpt-4o-mini`, 292 vectors) — this is NOT a CMS3 baseline and should not be treated as one | Critical |
| EV-10 | `scripts/run_langsmith_eval.py` | `max_concurrency=4` with no retry logic — will hit OpenAI rate limits on 27-question dataset | Low |

---

### C. Documentation Gaps (`docs/`)

| ID | Gap |
|----|-----|
| DOC-01 | `docs/features/eval-pipeline.md` — no technical doc exists for the eval module (`runner`, `metrics`, `report`, `diff`, `cli`) |
| DOC-02 | `docs/features/langsmith-integration.md` — no doc covering: dataset upload → `golden-v1` → experiment → evaluators → feedback loop |
| DOC-03 | `docs/features/observability.md` — exists but missing: streaming path token/cost gap (TR-06), per-node span attribute reference for nodes without `@traceable` yet, online evaluator setup steps |

---

## Part 2 — Implementation Plan

Each phase below is a self-contained unit. Complete and test one phase before starting the next. Each phase ends with a new or updated doc in `docs/features/`.

---

### Phase 1 — Complete Trace Anatomy (TR-01 → TR-06)

**Goal:** Every LangSmith run tree mirrors the full graph. Every node has a span. Root run carries latency + cost.

**Steps:**
1. Add `@traceable(run_type="chain")` to `rewrite_question`, `resolve_context` nodes
2. Add `@traceable(run_type="retriever")` + `attach_span_metadata({"k_summary": ..., "k_event": ..., "num_returned": ...})` to `retrieve_docs`
3. Add `@traceable(run_type="retriever")` + `attach_span_metadata({"num_input": ..., "num_kept": ..., "cutoff": ...})` to `rerank_docs`
4. Capture `latency_ms` in `invoke_with_observability` using `time.perf_counter()` and attach to root run metadata
5. Fix streaming cost gap (TR-06): wrap streaming path in `get_usage_metadata_callback` or add a cost-attach step after stream completion

**Deliverable:** Update `docs/features/observability.md` with corrected trace tree, per-node span attribute reference table, and streaming path cost capture design.

---

### Phase 2 — Environment Separation + Experiment Traceability (TR-07, TR-08)

**Goal:** Dev/eval/prod are separate LangSmith projects. Experiments link to git commits.

**Steps:**
1. Add `LANGCHAIN_PROJECT_DEV`, `LANGCHAIN_PROJECT_EVAL`, `LANGCHAIN_PROJECT_PROD` to `app/config.py` (with fallback to current `LANGCHAIN_PROJECT`)
2. Update `build_run_config` to select the correct project based on `env` param
3. In `run_langsmith_eval.py`, append `git rev-parse --short HEAD` to experiment prefix

**Deliverable:** `docs/features/langsmith-integration.md` — covers project setup, environment routing, how to find traces per environment in the UI.

---

### Phase 3 — Full Eval Metric Set (EV-01 → EV-05)

**Goal:** All 7 sprint metrics are computed and stored in eval results JSON.

**Steps:**
1. Add `context_precision` and `context_recall` to `compute_ragas_metrics` in `metrics.py` (Ragas `ContextPrecision`, `ContextRecall` — requires `reference` field from `ground_truth`)
2. Standardise `ground_truth` field across all 27 golden dataset entries (needed for `context_recall`)
3. Add `latency_ms` tracking in `runner.py` — record `time.perf_counter()` around `_invoke()` per question
4. Add `classification_accuracy` to `runner.py` — compare `query_type` result vs expected type in golden dataset (requires adding `expected_query_type` field to golden dataset for categorised questions)
5. Add LLM-as-judge `non_technical_clarity` scorer — prompt judges whether answer is free of jargon and readable by a non-technical manager (score 0–1, target > 0.75)
6. Fix threshold mismatch: update `answer_relevancy` target to `0.75` in `THRESHOLDS`
7. Add `latency_ms` and `non_technical_clarity` to `THRESHOLDS` and `GATE_CONFIG` in `diff.py`

**Deliverable:** `docs/features/eval-pipeline.md` — full technical doc: golden dataset schema, metric definitions, thresholds, how to run locally, how to update the baseline.

---

### Phase 4 — LangSmith Evaluator Coverage (EV-06, EV-07)

**Goal:** All computed metrics appear as named evaluator scores in LangSmith experiment UI.

**Steps:**
1. Add `faithfulness_evaluator` and `answer_relevancy_evaluator` to `langsmith_evaluators.py` — wrap the Ragas scores (run Ragas inline in evaluator or pass pre-computed scores via `outputs`)
2. Add `latency_evaluator` — reads `latency_ms` from `outputs` dict, returns score as raw ms value with threshold comment
3. Add `non_technical_clarity_evaluator` — reuse the LLM judge from Phase 3
4. Clarify `groundedness_evaluator` vs `faithfulness`: rename groundedness to `groundedness_llm_judge` and Ragas one to `faithfulness_ragas` in comments/key names
5. Update `ALL_EVALUATORS` list and `run_langsmith_eval.py` to include new evaluators
6. Add `max_concurrency=2` + `retry` logic in `run_langsmith_eval.py` to handle rate limits (EV-10)

**Deliverable:** Update `docs/features/langsmith-integration.md` with evaluator reference table, how scores map to LangSmith UI columns, and the feedback/annotation workflow.

---

### Phase 5 — Baseline Reset + Online Evaluation (EV-09, DOC-03)

**Goal:** `data/eval/baseline_results.json` reflects the real CMS3 pipeline. Online evaluator + monitor configured.

**Steps:**
1. Remove or archive `data/eval_results.json` (stale AMS Admin Tool run — EV-09)
2. Run full eval pipeline: `bash scripts/run_eval.sh --update-baseline` — commit new `data/eval/baseline_results.json` with all 7 metrics
3. Configure LangSmith online evaluator: sample 10% of `move-mind-prod` runs, apply `groundedness_llm_judge` continuously
4. Set LangSmith Monitor: alert if rolling 24h groundedness < 0.70
5. Document online eval setup steps in `docs/features/observability.md`

**Deliverable:** `docs/features/observability.md` updated with: online evaluator config, monitor alert setup, how to triage a monitor alert.

---

## Part 3 — Documentation Inventory

When each phase is implemented, the following docs are created/updated:

| Doc | Phase | Action |
|-----|-------|--------|
| `docs/features/observability.md` | Phase 1, 5 | Update (trace tree, per-node attributes, streaming cost, online eval) |
| `docs/features/langsmith-integration.md` | Phase 2, 4 | **Create** (project setup, environments, evaluators, feedback loop) |
| `docs/features/eval-pipeline.md` | Phase 3 | **Create** (golden dataset schema, metric definitions, thresholds, CLI usage, baseline workflow) |

---

## Part 4 — Summary of All Gaps by Priority

| Priority | IDs | Count |
|----------|-----|-------|
| Critical (block correct baselines) | EV-09 | 1 |
| High (missing coverage) | TR-01–TR-05, EV-01, EV-02, EV-06 | 8 |
| Medium | TR-06, TR-07, EV-03, EV-04, EV-08 | 5 |
| Low | TR-08, EV-05, EV-07, EV-10, DOC-01–DOC-03 | 6 |
