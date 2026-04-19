---
trigger: model_decision
description: SSE streaming contract from /api/v1/chat, frontend consumption patterns, TypeScript event types, and error handling
---

# Streaming Guide

The backend emits a **Server-Sent Events (SSE)** stream from `POST /api/v1/chat` when `stream: true`.
This document is the **single source of truth** for event types, their shapes, and how to consume them in React.

---

## Backend SSE Event Contract

Every event line is `data: <JSON>\n\n`. The stream ends with `data: [DONE]\n\n`.

### Event Types (in emission order)

| Event type   | When                              | Key fields                                           |
| ------------ | --------------------------------- | ---------------------------------------------------- |
| `session`    | Immediately after stream start    | `session_id: string`                                 |
| `status`     | On each LangGraph node start      | `node: string`                                       |
| `retrieval`  | After `retrieve_docs` node ends   | `retrieved_count: number`                            |
| `rerank`     | After `rerank_docs` node ends     | `reranked_count: number`                             |
| `token`      | Each LLM token during generation  | `content: string`                                    |
| `sources`    | Final event before `[DONE]`       | Full response payload (see below)                    |
| `[DONE]`     | Stream termination sentinel       | Literal string — not JSON                            |

### LangGraph Node Names (for `status` events)

```
classify_question
rewrite_question
resolve_context
retrieve_docs
rerank_docs
generate_answer
classify_issue
```

### `sources` event full shape

```json
{
  "type": "sources",
  "session_id": "string",
  "query_type": "string | null",
  "effective_question": "string",
  "retrieved_count": 0,
  "reranked_count": 0,
  "sources": [
    {
      "content": "string (max 400 chars)",
      "chunk_type": "string",
      "customer_id": "string",
      "execution_id": "string",
      "journey_id": "string",
      "page_path": "string",
      "action": "string",
      "step_order": "number | null",
      "target": "string",
      "decision_result": "any | null",
      "status": "string",
      "error_code": "string"
    }
  ],
  "issue_type": "bug | business_condition | unknown | null",
  "issue_confidence": "number | null",
  "issue_classification_reason": "string | null"
}
```

---

## TypeScript Types

```tsx
// src/interfaces/types.ts

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

export type IssueType = 'bug' | 'business_condition' | 'unknown' | null;

export interface SessionEvent   { type: 'session';   session_id: string }
export interface StatusEvent    { type: 'status';    node: string }
export interface RetrievalEvent { type: 'retrieval'; retrieved_count: number }
export interface RerankEvent    { type: 'rerank';    reranked_count: number }
export interface TokenEvent     { type: 'token';     content: string }
export interface SourcesEvent {
  type: 'sources';
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

export type SSEEvent =
  | SessionEvent
  | StatusEvent
  | RetrievalEvent
  | RerankEvent
  | TokenEvent
  | SourcesEvent;

export type NodeStatus = 'pending' | 'active' | 'done';

export type AgentNodeName =
  | 'classify_question'
  | 'rewrite_question'
  | 'resolve_context'
  | 'retrieve_docs'
  | 'rerank_docs'
  | 'generate_answer'
  | 'classify_issue';

export const AGENT_NODE_ORDER: AgentNodeName[] = [
  'classify_question',
  'rewrite_question',
  'resolve_context',
  'retrieve_docs',
  'rerank_docs',
  'generate_answer',
  'classify_issue',
];
```

---

## Frontend Consumption Pattern

Use `fetch` with a `ReadableStream` reader — **do not use `EventSource`** because this endpoint is `POST`.

```tsx
// src/api/chatClient.ts

export interface ChatStreamCallbacks {
  onSession: (sessionId: string) => void;
  onNodeStart: (node: string) => void;
  onRetrieval: (count: number) => void;
  onRerank: (count: number) => void;
  onToken: (token: string) => void;
  onSources: (event: SourcesEvent) => void;
  onDone: () => void;
  onError: (error: Error) => void;
}

export async function streamChat(
  message: string,
  sessionId: string | null,
  callbacks: ChatStreamCallbacks
): Promise<void> {
  const response = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId, stream: true }),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';  // keep incomplete line in buffer

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const raw = line.slice(6).trim();
      if (raw === '[DONE]') { callbacks.onDone(); return; }

      try {
        const event: SSEEvent = JSON.parse(raw);
        switch (event.type) {
          case 'session':   callbacks.onSession(event.session_id); break;
          case 'status':    callbacks.onNodeStart(event.node); break;
          case 'retrieval': callbacks.onRetrieval(event.retrieved_count); break;
          case 'rerank':    callbacks.onRerank(event.reranked_count); break;
          case 'token':     callbacks.onToken(event.content); break;
          case 'sources':   callbacks.onSources(event); break;
        }
      } catch {
        // malformed line — skip
      }
    }
  }
}
```

---

## `useSSEStream` Hook

```tsx
// src/hooks/useSSEStream.ts

export interface StreamState {
  isStreaming: boolean;
  tokenBuffer: string;
  activeNode: AgentNodeName | null;
  nodeStatuses: Record<AgentNodeName, NodeStatus>;
  retrievedCount: number | null;
  rerankedCount: number | null;
  error: string | null;
}

const INITIAL_NODES = Object.fromEntries(
  AGENT_NODE_ORDER.map((n) => [n, 'pending'])
) as Record<AgentNodeName, NodeStatus>;

export function useSSEStream() {
  const [state, setState] = useState<StreamState>({
    isStreaming: false,
    tokenBuffer: '',
    activeNode: null,
    nodeStatuses: { ...INITIAL_NODES },
    retrievedCount: null,
    rerankedCount: null,
    error: null,
  });

  const reset = () => setState({
    isStreaming: false,
    tokenBuffer: '',
    activeNode: null,
    nodeStatuses: { ...INITIAL_NODES },
    retrievedCount: null,
    rerankedCount: null,
    error: null,
  });

  return { state, setState, reset };
}
```

---

## Error Handling

```tsx
// Network errors
try {
  await streamChat(message, sessionId, callbacks);
} catch (error) {
  dispatch({ type: 'SET_ERROR', id: assistantId, error: 'Connection lost. Please try again.' });
}

// SSE mid-stream abort
const controller = new AbortController();
// Pass signal to fetch: { signal: controller.signal }
// Call controller.abort() if user navigates away or sends a new message
```

---

## Checklist

- [ ] Using `fetch` + `ReadableStream`, not `EventSource` (POST endpoint)
- [ ] Incomplete SSE lines buffered across `read()` calls
- [ ] `[DONE]` sentinel handled as a literal string, not parsed as JSON
- [ ] `session` event stores `session_id` in `ChatContext` for multi-turn
- [ ] `status` events update `nodeStatuses` — mark previous node `done` on new `active`
- [ ] Token buffer is local state — finalized to context only on `[DONE]`
- [ ] Network errors show user-friendly message with retry option
- [ ] `AbortController` used to cancel in-flight requests on unmount
