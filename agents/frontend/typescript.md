---
trigger: glob
description: TypeScript strict typing rules, naming conventions, and Move Mind AI domain types — loaded when editing TS/TSX files
globs: "frontend/src/**/*.ts,frontend/src/**/*.tsx"
---

# TypeScript Rules

## Strict Typing

- No unjustified `any` types
- Define interfaces for all props and return types
- Export types that others need

```tsx
// ❌ NEVER
function process(data: any) { ... }
const items = response.data;

// ✅ ALWAYS
function process(data: ChatRequest): ChatResponse { ... }
const sources: SourceDocument[] = event.sources;
```

## Props Interface

Define at top of component file:

```tsx
interface MessageBubbleProps {
  message: Message;
  nodeStatuses?: Record<AgentNodeName, NodeStatus>;
  isStreaming?: boolean;
}
```

## Naming Conventions

| Type       | Convention                 | Example                                       |
| ---------- | -------------------------- | --------------------------------------------- |
| Components | PascalCase                 | `MessageBubble`, `AgentNodeBadge`             |
| Hooks      | camelCase, prefix `use`    | `useChat`, `useSSEStream`, `usePreference`    |
| Utilities  | camelCase                  | `formatConfidence`, `parseSSELine`            |
| Constants  | SCREAMING_SNAKE_CASE       | `AGENT_NODE_ORDER`, `MAX_RETRIES`             |
| Interfaces | PascalCase                 | `Message`, `SourceDocument`, `SSEEvent`       |
| Files      | PascalCase matching export | `MessageBubble.tsx`, `MessageBubble.hook.tsx` |

---

## Core Domain Types (src/interfaces/types.ts)

All shared types live in `src/interfaces/types.ts`. Import from there — never re-declare locally.

```tsx
// Agent pipeline
export type NodeStatus = "pending" | "active" | "done";
export type AgentNodeName =
  | "classify_question"
  | "rewrite_question"
  | "resolve_context"
  | "retrieve_docs"
  | "rerank_docs"
  | "generate_answer"
  | "classify_issue";

export const AGENT_NODE_ORDER: AgentNodeName[] = [
  "classify_question",
  "rewrite_question",
  "resolve_context",
  "retrieve_docs",
  "rerank_docs",
  "generate_answer",
  "classify_issue",
];

// Issue classification
export type IssueType = "bug" | "business_condition" | "unknown" | null;

// Source document from RAG pipeline
export interface SourceDocument {
  content: string;
  chunk_type: string;
  customer_id: string;
  execution_id: string;
  journey_id: string;
  page_path: string;
  action: string;
  step_order: number | null;
  target: string;
  decision_result: unknown;
  status: string;
  error_code: string;
}

// Chat message
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  sources?: SourceDocument[];
  issueType?: IssueType;
  issueConfidence?: number | null;
  issueClassificationReason?: string | null;
}

// API request/response
export interface ChatRequest {
  message: string;
  session_id: string | null;
  stream: boolean;
}

// SSE events — see STREAMING.md for full contract
export type SSEEvent =
  | { type: "session"; session_id: string }
  | { type: "status"; node: AgentNodeName }
  | { type: "retrieval"; retrieved_count: number }
  | { type: "rerank"; reranked_count: number }
  | { type: "token"; content: string }
  | SourcesEvent;

export interface SourcesEvent {
  type: "sources";
  session_id: string;
  query_type: string | null;
  effective_question: string;
  retrieved_count: number;
  reranked_count: number;
  sources: SourceDocument[];
  issue_type: IssueType;
  issue_confidence: number | null;
  issue_classification_reason: string | null;
}
```
