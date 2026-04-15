# Move Mind AI — Eval Sprint Plan (2 Weeks)

> Sprint start: 2026-04-10
> Branch: feat/eval
> Goal: Produce a reliable system with measurable, repeatable metrics on every run.

---

## Legend

| Status | Meaning |
|--------|---------|
| 🔴 Not Started | Planned, not begun |
| 🟡 In Progress | Currently being worked on |
| 🟢 Done | Completed and verified |
| ⚪ Blocked | Waiting on dependency |

---

## Success Criteria

The sprint is complete when:
- [ ] All tests pass (`pytest tests/`)
- [ ] Eval pipeline runs in one command (`pytest tests/eval/` or `scripts/run_eval.sh`)
- [ ] Metrics report generated automatically after each eval run
- [ ] All 7 metrics tracked per run (see table below)
- [ ] Baseline scores established and committed to `data/eval/`

---

## Metrics We Track (Every Run)

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| Faithfulness | Answer grounded in retrieved context (no hallucination) | > 0.80 |
| Answer Relevancy | Answer actually answers the question asked | > 0.75 |
| Context Precision | Retrieved chunks are relevant (low noise) | > 0.70 |
| Context Recall | All needed info was retrieved | > 0.65 |
| E2E Latency | Time from question to full answer | < 8s |
| Classification Accuracy | retrieve vs rewrite correctly assigned | > 0.90 |
| Non-Technical Clarity | LLM-as-judge: explanation quality for agents | > 0.75 |

---

## Week 1 — Fix Foundation + Build Eval Infrastructure

### Days 1–2: Fix Broken Baseline

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Fix `tests/test_chains.py` — wrong import path (F-01) | | 🔴 Not Started | Should import from `app.chains.classify_chain` etc |
| Fix `tests/test_graphs.py` — `build_agent_graph` → `build_rag_graph` (F-02) | | 🔴 Not Started | |
| Fix `tests/test_rag.py` — align imports with real function names (F-03) | | 🔴 Not Started | |
| Fix `scripts/ingest.py` — call `build_vectorstore()` not `ingest()` (F-04) | | 🔴 Not Started | |
| Smoke test: full pipeline runs from question → answer | | 🔴 Not Started | |

### Days 3–5: Build Golden Eval Dataset

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Create `data/eval/golden_dataset.json` schema | | 🔴 Not Started | Fields: question, expected_answer, expected_sources, category, cid |
| Write 5–8 CID lookup questions | | 🔴 Not Started | e.g. "What happened to CID 7093495?" |
| Write 5–8 root cause / why questions | | 🔴 Not Started | e.g. "Why did this journey fail?" |
| Write 5–8 business condition questions | | 🔴 Not Started | e.g. "Why was this customer blocked?" |
| Write 5–8 API timeline questions | | 🔴 Not Started | e.g. "Show me all APIs called in this journey" |
| Write 5–8 multi-turn follow-up questions | | 🔴 Not Started | Depends on prior turn context |

### Days 6–7: Implement Ragas Eval Pipeline

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Create `app/eval/` module | | 🔴 Not Started | |
| `app/eval/runner.py` — drive questions through graph, collect answers | | 🔴 Not Started | |
| `app/eval/metrics.py` — compute Ragas scores (faithfulness, relevancy, precision, recall) | | 🔴 Not Started | |
| `app/eval/report.py` — JSON + human-readable summary output | | 🔴 Not Started | |
| `tests/eval/test_eval_pipeline.py` — pytest entry point for eval | | 🔴 Not Started | |

---

## Week 2 — Metrics, Reliability Fixes, Showcase

### Days 8–9: Observability

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Activate LangSmith tracing on graph runs (F-07) | | 🔴 Not Started | Already in config, needs wiring |
| Tag runs: session_id, query_type, CID | | 🔴 Not Started | Filter by scenario in LangSmith |
| Add LLM-as-judge scoring for non-technical clarity | | 🔴 Not Started | Separate judge prompt |

### Days 10–11: Reliability Fixes from Eval Findings

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Run eval against golden dataset — record baseline scores | | 🔴 Not Started | |
| Identify top 3 failure modes from eval output | | 🔴 Not Started | |
| Fix retrieval/generation issues found | | 🔴 Not Started | TBD based on findings |
| Re-run eval — confirm improvement | | 🔴 Not Started | |

### Days 12–13: CI Eval Gate

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| `scripts/run_eval.sh` — one-command eval run | | 🔴 Not Started | |
| Fail eval if metrics below thresholds | | 🔴 Not Started | |
| Integrate with pytest (`pytest tests/eval/`) | | 🔴 Not Started | |

### Day 14: Baseline Report

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Commit baseline `data/eval/baseline_results.json` | | 🔴 Not Started | |
| Write `docs/eval-results.md` — first metrics report | | 🔴 Not Started | Per-category scores, pass/fail per question |
| Update this doc: all tasks to 🟢 Done | | 🔴 Not Started | |

---

## Decisions & Notes

> Add any design decisions, pivots, or important context here as the sprint progresses.

- **2026-04-10**: Sprint started on branch `feat/eval`. Beginning with broken test fixes before eval build.
