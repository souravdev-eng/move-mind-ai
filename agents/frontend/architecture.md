---
trigger: glob
globs: "frontend/src/**"
description: Architecture decisions — where to place new code, when to split files, atomic design classification guide for the Move Mind AI agentic + generative UI
---

# Architecture Decision Guide

Use this when creating new components or files to decide placement and structure. This project is a **streaming AI debugging assistant** — UI responds to real-time SSE events from a LangGraph agent pipeline.

## Atomic Classification

| Complexity           | Directory        | Example                                | Storybook? |
| -------------------- | ---------------- | -------------------------------------- | ---------- |
| Single UI element    | `src/atoms/`     | Button, Badge, StatusDot, TypingDots   | Planned    |
| Composition of atoms | `src/molecules/` | ChatInput, SourceCard, AgentNodeBadge  | Planned    |
| Complex feature      | `src/organisms/` | ChatThread, AgentPipeline, SourcePanel | No         |
| Route-level view     | `src/pages/`     | ChatPage                               | No         |

## Code Placement

| What you're creating            | Where it goes     |
| ------------------------------- | ----------------- |
| Pure helper function            | `src/utils/`      |
| Shared type/interface           | `src/interfaces/` |
| Backend API client (REST + SSE) | `src/api/`        |
| Global state (chat, session)    | `src/context/`    |
| Shared hook                     | `src/hooks/`      |
| SSE stream consumer hook        | `src/hooks/`      |

> **No Redux, no TanStack Query, no Firebase.** This project uses React Context + `useReducer` for global chat state, and native `EventSource` / `fetch` for SSE streaming.

## When to Split Files

| File Type    | Max Lines | Split Into                               |
| ------------ | --------- | ---------------------------------------- |
| `.tsx`       | 400       | `Layout/` subfolder with sub-components  |
| `.hook.tsx`  | 400       | `hooks/` subfolder with sub-hooks        |
| `.style.tsx` | 300       | Group related styles or split by section |

## Required Files Per Component

```
ComponentName/
├── ComponentName.tsx          # JSX + props interface
├── ComponentName.style.tsx    # Styled components (theme only)
├── ComponentName.hook.tsx     # Business logic (if needed)
└── index.ts                   # Re-export
```

## Full `src/` Directory Map

```
src/
├── atoms/                # Button, Badge, StatusDot, TypingDots, StreamingCursor
├── molecules/            # ChatInput, SourceCard, AgentNodeBadge, IssueClassBadge
├── organisms/            # ChatThread, AgentPipeline, SourcePanel, MessageBubble
├── pages/                # ChatPage
├── api/                  # chatClient.ts — REST + SSE client to /api/v1/chat
├── context/              # ChatContext.tsx — messages, session_id, streaming state
├── hooks/                # useChat.ts, useSSEStream.ts, useAgentPipeline.ts
├── interfaces/           # types.ts — Message, SSEEvent, SourceDocument, AgentNode
├── utils/                # formatters, markdown parsers, etc.
├── App.tsx
├── index.tsx
└── theme.ts
```

## Data Flow

```
User types message
      │
      ▼
ChatInput (molecule) → useChat hook
      │
      ▼
chatClient.ts → POST /api/v1/chat  (stream: true)
      │
      ▼  SSE stream
useSSEStream hook parses events:
  ├─ session   → store session_id in ChatContext
  ├─ status    → update AgentPipeline display
  ├─ retrieval → update pipeline stats
  ├─ rerank    → update pipeline stats
  ├─ token     → append to streaming message buffer
  ├─ sources   → attach SourceDocument[] to message
  └─ [DONE]    → mark message complete
      │
      ▼
ChatThread (organism) renders:
  ├─ MessageBubble (streaming text + cursor)
  ├─ AgentPipeline (node progress visualization)
  └─ SourcePanel (citations + issue classification)
```
