---
trigger: glob
globs: "frontend/src/**"
description: Architecture decisions — where to place new code, when to split files, atomic design classification guide for the Move Mind AI agentic + generative UI
---

# Architecture Decision Guide

Use this when creating new components or files to decide placement and structure. This project is a **streaming AI debugging assistant** — UI responds to real-time SSE events from a LangGraph agent pipeline.

## Atomic Classification

| Complexity           | Directory        | Example                                            | Storybook? |
| -------------------- | ---------------- | -------------------------------------------------- | ---------- |
| Single UI element    | `src/atoms/`     | StatusBadge, ConfidenceChip, KPIStat               | Planned    |
| Composition of atoms | `src/molecules/` | PageHeader, SectionTabs, EmptyState, ToolCallBlock | Planned    |
| Complex feature      | `src/organisms/` | MessageList, EvidenceDrawer, DescriptorForm        | No         |
| Route-level view     | `src/pages/`     | DashboardPage, InvestigatePage, AppShell           | No         |

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
├── atoms/                # Single UI elements: StatusBadge, ConfidenceChip, KPIStat
├── molecules/            # Composed UI: PageHeader, SectionTabs, EmptyState,
│                         #   ToolCallBlock, DescriptorField
├── organisms/            # Complex features: MessageList, EvidenceDrawer,
│                         #   ScopePanel, DescriptorForm
├── pages/                # Route-level views — each follows the ComponentName/ subdir pattern
│   ├── shell/            #   AppShell/, TopBar/, LeftRail/, Breadcrumbs/, OrgSwitcher/, ProjectSwitcher/
│   ├── dashboard/        #   DashboardPage/
│   ├── onboarding/       #   OnboardingWizard/
│   ├── ComingSoonPage/
│   └── project/
│       ├── logs/         #   ConnectorsPage/, IngestionRunsPage/, SchemaPage/, LogsTabs/
│       ├── integrations/ #   IntegrationsHub/, JiraPage/
│       ├── code-context/ #   McpServersPage/, McpServerDetailPage/
│       └── ...           #   OverviewPage/, InvestigatePage/, ConversationsPage/, SettingsPage/
├── api/                  # (reserved) chatClient.ts — REST + SSE client
├── context/              # (reserved) ChatContext.tsx — global chat state
├── hooks/                # useActiveProject.ts, useSimulatedStream.ts
├── interfaces/           # domain.ts — all domain types (Org, Project, ChatMessage…)
├── mocks/                # Static fixture data for all domain entities
├── utils/                # (reserved) formatters, parsers
├── test/                 # setup.ts, renderApp.tsx
├── router.tsx            # createBrowserRouter route tree
├── App.tsx
├── index.tsx
└── theme/                # MUI theme tokens and ThemeProvider
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
