# Week 1 Plan — Stabilize & Measure

> Sprint: 2026-04-10 to 2026-04-17
> Branch: feat/eval
> Goal: Make the core investigation output reliable and measurable for the manager use case. No new features until the foundation is solid.

---

## Legend

| Status | Meaning |
|--------|---------|
| 🔴 Not Started | Planned, not begun |
| 🟡 In Progress | Currently being worked on |
| 🟢 Done | Completed and verified |
| ⚪ Blocked | Waiting on dependency |

---

## Definition of Done (Week 1)

- [ ] All tests pass (`pytest tests/`)
- [ ] Plain English answers reviewed manually for manager audience (5 real CID questions)
- [ ] Golden dataset committed (`data/eval/golden_dataset.json`) — min 27 Q&A pairs
- [ ] Baseline eval metrics committed (`data/eval/baseline_results.json`)
- [ ] Issue classifier working and included in manager response
- [ ] `docs/system-audit.md` statuses updated for every completed item

---

## Day 1 — Fix Broken Baseline

> Nothing should be broken before we build on it.

| # | Task | Audit Ref | Status |
|---|------|-----------|--------|
| 1.1 | Fix `tests/test_chains.py` — align imports with real module paths | T-01 | 🟢 Done |
| 1.2 | Fix `tests/test_graphs.py` — `build_agent_graph` → `build_rag_graph` | T-02 | 🟢 Done |
| 1.3 | Fix `tests/test_rag.py` — align with real function names in `app/rag/ingestion.py` | T-03 | 🟢 Done |
| 1.4 | Fix `scripts/ingest.py` — call `build_vectorstore()` not `ingest()` | T-04 | 🟢 Done |
| 1.5 | Smoke test: full question → answer pipeline end to end | — | 🟢 Done |

---

## Day 2 — Tune Plain English Prompt for Manager

> The current `ANSWER_PROMPT` generates a technical answer with chunk metadata. A manager needs a clear, jargon-free narrative.

| # | Task | Audit Ref | Status |
|---|------|-----------|--------|
| 2.1 | Rewrite `ANSWER_PROMPT` with manager persona — no jargon, narrative format | P-01 | 🟢 Done |
| 2.2 | Separate "plain English summary" from "technical evidence" in response structure | P-01 | 🟢 Done |
| 2.3 | Add `explanation_mode` to `GraphState` (`"manager"` \| `"developer"`) — foundation for dual mode | P-01, P-06 | 🟢 Done |
| 2.4 | Manual spot-check: run 5 real CID questions, review plain English quality | — | 🟢 Done |

---

## Day 3 — Build Golden Eval Dataset

> These become the benchmark we run forever. Questions are written from the manager's perspective.

| # | Task | Category | Status |
|---|------|----------|--------|
| 3.1 | Define `data/eval/golden_dataset.json` schema (`question`, `expected_answer`, `category`, `cid`) | — | 🟢 Done |
| 3.2 | Write 6 CID investigation questions — "What happened to CID X?" | CID Lookup | 🟢 Done |
| 3.3 | Write 6 root cause questions — "Why was this journey blocked?" | Root Cause | 🟢 Done |
| 3.4 | Write 5 business condition questions — "Why did this agent get this message?" | Business Condition | 🟢 Done |
| 3.5 | Write 5 API timeline questions — "What APIs were called in this journey?" | API Timeline | 🟢 Done |
| 3.6 | Write 5 multi-turn follow-up questions — depend on prior turn context | Multi-turn | 🟢 Done |

**Target: 27 golden Q&A pairs across 5 categories.**

---

## Day 4 — Build Eval Pipeline + Run Baseline

> Wire up Ragas. Run the golden dataset. Get the first real numbers.

| # | Task | Audit Ref | Status |
|---|------|-----------|--------|
| 4.1 | Create `app/eval/runner.py` — drives each golden question through the graph | T-07 | 🟢 Done |
| 4.2 | Create `app/eval/metrics.py` — computes Ragas scores (faithfulness, relevancy, precision, recall) | T-07 | 🟢 Done |
| 4.3 | Create `app/eval/report.py` — writes JSON + human-readable summary | T-07 | 🟢 Done |
| 4.4 | Run eval against full golden dataset | T-08 | 🟢 Done |
| 4.5 | Commit baseline results to `data/eval/baseline_results.json` | T-08 | 🟢 Done |

### Metrics Targets vs Baseline

| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| jargon_leak_rate | **0.000** | < 0.10 | ✅ Perfect |
| keyword_hit_rate | 0.606 | > 0.80 | ⚠️ Below |
| Faithfulness | 0.637 | > 0.80 | ⚠️ Below |
| Answer Relevancy | 0.512 | > 0.70 | ⚠️ Below |

**Baseline findings (2026-04-10):**
- Jargon leak is zero across all 27 questions — manager prompt works perfectly
- cid_lookup is strong (kw=0.892, faith=0.953) — straightforward factual queries work well
- root_cause faithfulness is low (0.348) — LLM reasons beyond retrieved evidence on "why" questions
- multi_turn keyword_hit lowest (0.370) — context not fully carrying forward in follow-ups
- keyword misses are partly a vocabulary issue (synonyms used vs exact expected words)

---

## Day 5 — Issue Classifier (Bug vs Business Condition)

> First piece of new product logic. Manager sees this before deciding to create a ticket.

| # | Task | Audit Ref | Status |
|---|------|-----------|--------|
| 5.1 | Design classification prompt — signals that distinguish a bug from a business condition | P-04 | 🔴 Not Started |
| 5.2 | Add `classify_issue` node to LangGraph (runs after `generate_answer`) | P-04 | 🔴 Not Started |
| 5.3 | Add `issue_type` to `GraphState` (`"bug"` \| `"business_condition"` \| `"unknown"`) | P-04 | 🔴 Not Started |
| 5.4 | Include `issue_type` + confidence in manager response | P-04 | 🔴 Not Started |
| 5.5 | Add 5 classification Q&As to golden dataset, re-run eval | T-08 | 🔴 Not Started |

---

## Week 2 Preview (Do Not Start Yet)

| Day | Focus |
|-----|-------|
| Day 6–7 | Jira tool — client, config, ticket payload builder |
| Day 8–9 | Deep technical report generator + steps to reproduce |
| Day 10 | Manager-triggered "create ticket" conversation flow end to end |

---

## Notes & Decisions

> Add any pivots, blockers, or decisions here as the week progresses.

- **2026-04-10**: Week 1 plan locked. Starting with Day 1 (fix broken baseline).
