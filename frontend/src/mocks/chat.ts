import { type ChatMessage, type EvidenceItem } from "@/interfaces/domain";

export const cannedTranscript: ChatMessage[] = [
  {
    id: "m1",
    role: "user",
    content: "Why is CID 7093495 stuck on step 4?",
    createdAtIso: "2026-04-19T08:10:00Z",
  },
  {
    id: "m2",
    role: "tool",
    content: "Searched logs for CID 7093495 in the last 24h.",
    toolCall: {
      name: "search_logs",
      input: '{ query: "CID 7093495", filters: { last: "24h" } }',
      output: "18 events found across 1 execution group (execution_id exec_5521).",
      latencyMs: 412,
    },
    createdAtIso: "2026-04-19T08:10:04Z",
  },
  {
    id: "m3",
    role: "tool",
    content: "Fetched the full event group for execution exec_5521.",
    toolCall: {
      name: "get_event_group",
      input: '{ correlation_id: "exec_5521" }',
      output: "18 events between 07:40 and 07:44; halts after step_order 4.",
      latencyMs: 220,
    },
    createdAtIso: "2026-04-19T08:10:06Z",
  },
  {
    id: "m4",
    role: "tool",
    content: "Pulled code context for the condition evaluator.",
    toolCall: {
      name: "get_code_context",
      server: "acme/cms3 code server",
      input: '{ symbolOrFile: "evaluateCondition" }',
      output: "Found in src/graph/condition.ts — null-ref path on missing actor.",
      latencyMs: 214,
    },
    createdAtIso: "2026-04-19T08:10:09Z",
  },
  {
    id: "m5",
    role: "assistant",
    content:
      "Customer 7093495's journey halted on step 4 because the condition evaluator received a null actor reference. This looks like a bug introduced in CMS3 v4.12 — `evaluateCondition` no longer guards against an unset `actor` field before dereferencing it. Evidence: execution_id exec_5521 between 07:40 and 07:44 (18 events). Recent commit 9a2f4e1 by ana@ touched this path on 2026-04-17.",
    verdict: "bug",
    createdAtIso: "2026-04-19T08:10:13Z",
  },
];

export const cannedEvidence: EvidenceItem[] = [
  {
    id: "ev_01",
    source: "cms3 structured logs",
    timestampIso: "2026-04-19T07:40:12Z",
    snippet: "step_order=4 level=error error_code=E_COND_NULL message='actor undefined'",
    correlationId: "exec_5521",
  },
  {
    id: "ev_02",
    source: "cms3 structured logs",
    timestampIso: "2026-04-19T07:40:11Z",
    snippet: "step_order=3 level=info route_entered page_path=/onboard/confirm",
    correlationId: "exec_5521",
  },
  {
    id: "ev_03",
    source: "acme/cms3 code server",
    timestampIso: "2026-04-17T14:10:00Z",
    snippet: "commit 9a2f4e1 — refactor evaluateCondition (ana@)",
    correlationId: "git",
  },
];
