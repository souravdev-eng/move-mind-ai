# Book Map — What To Read From Your Shelf Each Week

> Maps the O'Reilly / SRE books you already own to the sprint weeks where each chapter is directly load-bearing. Read only the mapped chapters for the current week — don't try to read a book cover to cover.

**Honest caveat:** I cite chapters **by theme**, not by exact chapter number, because book editions shift numbering. Open your book's TOC and grep for the theme title — you'll find it.

---

## Your Shelf

| Book | Role in this project |
|------|---------------------|
| **Google SRE Book** | Production-grade thinking — reliability, monitoring, on-call, toil |
| **Designing Data-Intensive Applications** (Kleppmann) | System-design fundamentals — the substrate under any AI system |
| **LLMOps** (O'Reilly) | Operating LLM systems specifically — training, serving, monitoring, drift |
| **Generative AI Design Patterns** (O'Reilly) | Reusable patterns — RAG, agents, routing, guardrails |
| **LLM Security** (O'Reilly) | Prompt injection, data leakage, supply chain, OWASP LLM Top 10 |
| **Fundamentals of Data Engineering** (Reis & Housley) | The data side — ingestion, transformation, serving, storage, DataOps |

---

## Week 2 — Observability & Eval Hardening (Current)

> Read these **before** Day 1. ~4–6 hours of reading total. Skim hard, don't deep-read — you'll revisit as tasks surface.

| Book | Chapters to read (by theme) | Why this week |
|------|------------------------------|---------------|
| **SRE Book** | "Monitoring Distributed Systems" (the four golden signals) | Foundational vocabulary for Part A.1 of the week plan |
| **SRE Book** | "Service Level Objectives" | Translates directly to our regression gate — SLOs are thresholds with consequences |
| **SRE Book** | "Practical Alerting from Time-Series Data" | Our online evaluator + Monitor in LangSmith is exactly this pattern |
| **LLMOps** | The "Monitoring" / "Observability" chapter | LLM-specific extensions to SRE — token drift, prompt drift, cost tracking |
| **LLMOps** | The "Evaluation" chapter | Online vs offline eval, LLM-as-judge patterns — reinforces Part A.5 |
| **Generative AI Design Patterns** | The chapter covering the **"Evaluation" or "Observability" pattern** | Pattern-oriented view of what you're wiring |
| **DDIA** | Ch 1 "Reliable, Scalable, Maintainable Applications" (if you haven't read it) | 20-page chapter that reframes every design decision — the single highest ROI chapter in your library |

**What you should be able to say** after these readings:
- "A golden-signal dashboard for our graph tracks latency, traffic, errors, and saturation — and for LLMs I add two more: cost and quality."
- "Our regression gate is an SLO on `faithfulness >= baseline - 3%`. When it trips, CI is the enforcement mechanism."
- "Offline eval is our canary, online eval is our smoke detector."

---

## Week 1 — Stabilize & Measure (Already Done — Back-reference)

| Book | Chapters | Why |
|------|----------|-----|
| **LLMOps** | "Evaluation" chapter | The conceptual foundation for Ragas + golden dataset |
| **Fundamentals of Data Engineering** | "DataOps" + "Data Quality" chapters | Golden-dataset curation is dataset engineering |
| **Generative AI Design Patterns** | The "RAG" chapter | The pattern you're stabilizing |

---

## Week 3 (Preview) — Agentic Control Flow (CRAG + Self-RAG)

| Book | Chapters | Why |
|------|----------|-----|
| **Generative AI Design Patterns** | Chapters on "Agents", "Routing", "Self-Correction" / "Reflection" | CRAG + groundedness self-check are textbook instances of these patterns |
| **SRE Book** | "Handling Overload" + "Addressing Cascading Failures" | Loops can amplify latency and cost — SRE thinking keeps you honest |
| **LLM Security** | "Prompt Injection" + "Output Handling" chapters | Agentic loops widen the attack surface — read *before* shipping loops |
| **DDIA** | "Consistency and Consensus" (skim) | The re-retrieval loop is a consistency problem in disguise |

---

## Later Weeks — Mapped Preemptively

### When we ship to real users (prod hardening week)
- **SRE Book**: "Release Engineering", "Emergency Response", "Postmortem Culture" — adopt postmortems from day 1 of prod
- **LLM Security**: whole book, prioritized top to bottom — OWASP LLM Top 10 is now your checklist
- **DDIA**: "Encoding and Evolution" — your graph state schema *will* evolve; plan the migration path

### When Jira integration + ticketing ship
- **Fundamentals of Data Engineering**: "Serving" chapter — tickets are downstream consumers of your pipeline
- **Generative AI Design Patterns**: the "Tool Use" / "Function Calling" chapter

### When we add multi-tenancy / scale
- **DDIA**: "Partitioning", "Replication", "Batch Processing", "Stream Processing"
- **SRE Book**: "Load Balancing at the Frontend", "Managing Critical State"

### When ingestion grows beyond POC
- **Fundamentals of Data Engineering**: "Ingestion", "Transformation", "Storage" chapters — your whole vector-store pipeline is this book
- **DDIA**: "Storage and Retrieval" — vector DB internals suddenly make sense

---

## Reading Discipline (How To Not Waste Your Books)

1. **One chapter per evening, max.** Dense books; diminishing returns past 60 min.
2. **Mark up physically.** Underline one sentence per page. If you can't find one, re-read the page.
3. **Write a 3-bullet summary** at the end of each chapter — paste it into the week's plan under "Notes & Decisions". This is how book knowledge becomes project knowledge.
4. **If a chapter feels disconnected from this week's work**, skip it — come back when the relevant week arrives. Off-topic reading decays before you use it.
5. **DDIA is special** — it rewards re-reading the same chapter 6 months apart. Expect to return to it.

---

## Notes

> Log which chapters you actually read + what stuck. Building this habit *is* part of the senior-path skill.

- (fill in as you go)
