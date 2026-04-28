---
trigger: glob
globs: "frontend/src/**"
description: State management rules — ChatContext, streaming local state, localStorage preferences. No Redux, no TanStack Query, no Firebase.
---

# State Management

> **This project does NOT use Redux Toolkit, TanStack Query, or Firebase.** State is managed with React Context + `useReducer` for global chat state, and native `fetch` / `EventSource` for SSE streaming.

## Decision Matrix

| Data Type          | Use                     | Example                                  |
| ------------------ | ----------------------- | ---------------------------------------- |
| **Chat messages**  | `ChatContext` + reducer | Message history, session_id              |
| **Streaming**      | Local state in hook     | Token buffer, active node, stream status |
| **Agent pipeline** | Local state in hook     | Node statuses, retrieval/rerank counts   |
| **Local UI**       | `useState`              | Input value, source panel open/closed    |
| **Preferences**    | `localStorage`          | Dark/light mode, collapsed panel state   |

---

## ChatContext — Global Chat State

All persistent chat state lives here. Wrap the app with `ChatProvider`.

```tsx
// src/context/ChatContext.tsx
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  sources?: SourceDocument[];
  issueType?: string | null;
  issueConfidence?: number | null;
}

interface ChatState {
  sessionId: string | null;
  messages: Message[];
  isLoading: boolean;
}

type ChatAction =
  | { type: "SET_SESSION"; sessionId: string }
  | { type: "ADD_USER_MESSAGE"; content: string }
  | { type: "ADD_ASSISTANT_MESSAGE"; id: string }
  | { type: "APPEND_TOKEN"; id: string; token: string }
  | {
      type: "FINALIZE_MESSAGE";
      id: string;
      sources: SourceDocument[];
      issueType: string | null;
      issueConfidence: number | null;
    }
  | { type: "SET_ERROR"; id: string; error: string };

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case "SET_SESSION":
      return { ...state, sessionId: action.sessionId };
    case "ADD_USER_MESSAGE":
      return {
        ...state,
        isLoading: true,
        messages: [
          ...state.messages,
          { id: crypto.randomUUID(), role: "user", content: action.content },
        ],
      };
    case "ADD_ASSISTANT_MESSAGE":
      return {
        ...state,
        messages: [
          ...state.messages,
          { id: action.id, role: "assistant", content: "", isStreaming: true },
        ],
      };
    case "APPEND_TOKEN":
      return {
        ...state,
        messages: state.messages.map((m) =>
          m.id === action.id ? { ...m, content: m.content + action.token } : m,
        ),
      };
    case "FINALIZE_MESSAGE":
      return {
        ...state,
        isLoading: false,
        messages: state.messages.map((m) =>
          m.id === action.id
            ? {
                ...m,
                isStreaming: false,
                sources: action.sources,
                issueType: action.issueType,
                issueConfidence: action.issueConfidence,
              }
            : m,
        ),
      };
    default:
      return state;
  }
}
```

---

## Streaming State — Local to `useChat` Hook

Keep stream-specific ephemeral state local to the hook — do **not** lift it to context.

```tsx
// src/hooks/useChat.ts
export function useChat() {
  const { state, dispatch } = useChatContext();
  const [activeNodes, setActiveNodes] = useState<Record<string, NodeStatus>>({});
  const [retrievalCount, setRetrievalCount] = useState<number | null>(null);

  const sendMessage = async (question: string) => {
    dispatch({ type: "ADD_USER_MESSAGE", content: question });
    const assistantId = crypto.randomUUID();
    dispatch({ type: "ADD_ASSISTANT_MESSAGE", id: assistantId });
    setActiveNodes({});

    const response = await fetch("/api/v1/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: question, session_id: state.sessionId, stream: true }),
    });

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const lines = decoder.decode(value).split("\n");
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const raw = line.slice(6).trim();
        if (raw === "[DONE]") break;

        const event: SSEEvent = JSON.parse(raw);
        handleSSEEvent(event, assistantId, dispatch, setActiveNodes, setRetrievalCount);
      }
    }
  };

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    activeNodes,
    retrievalCount,
    sendMessage,
  };
}
```

---

## Local UI State

Use `useState` for anything scoped to a single component.

```tsx
// ✅ Input value — local, not shared
const [inputValue, setInputValue] = useState("");

// ✅ Panel open/closed — local to organism
const [isSourcePanelOpen, setIsSourcePanelOpen] = useState(false);

// ✅ Derived values — never store in state
const hasMessages = messages.length > 0; // derived
const lastMessage = messages[messages.length - 1]; // derived
```

---

## Preferences — localStorage

Persist lightweight user preferences directly in `localStorage` via a small hook.

```tsx
// src/hooks/usePreference.ts
export function usePreference<T>(key: string, defaultValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : defaultValue;
    } catch {
      return defaultValue;
    }
  });

  const set = (next: T) => {
    setValue(next);
    localStorage.setItem(key, JSON.stringify(next));
  };

  return [value, set] as const;
}

// Usage
const [isDark, setIsDark] = usePreference("theme", false);
```

---

## Anti-Patterns

```tsx
// ❌ Never lift streaming buffer to context — too many re-renders
dispatch({ type: 'APPEND_TOKEN', token }); // per token — bad at context level

// ✅ Buffer tokens locally in hook, finalize to context once complete
const [buffer, setBuffer] = useState('');
setBuffer((b) => b + token);                // fast local update
// then on [DONE]:
dispatch({ type: 'FINALIZE_MESSAGE', content: buffer, ... });

// ❌ Don't derive values with useEffect + useState
const [hasError, setHasError] = useState(false);
useEffect(() => setHasError(messages.some((m) => m.isError)), [messages]);

// ✅ Derive inline
const hasError = messages.some((m) => m.isError);
```

---

## Checklist

- [ ] Global chat state (messages, session) lives in `ChatContext`
- [ ] Streaming token buffer is local state in `useChat`, not context
- [ ] Agent pipeline node states are local to `useChat` / `useAgentPipeline`
- [ ] No duplicate state — `messages` is the single source of truth
- [ ] Derived values computed inline with `useMemo`, not stored in state
- [ ] User preferences use `usePreference` with `localStorage`
- [ ] Session ID persisted in context and re-sent on every turn
