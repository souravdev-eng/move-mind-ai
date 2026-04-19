---
trigger: model_decision
description: Generative and agentic UI patterns — how to build components that respond to live AI output, agent pipeline visualization, dynamic rendering
---

# Generative UI Guide

Move Mind AI renders UI **dynamically in response to live AI agent events**.
This is distinct from a static chat UI — the interface evolves as the LangGraph pipeline progresses.

---

## Core Principle: UI as Agent Mirror

Each SSE event type maps to a specific UI update:

| SSE Event    | UI Reaction                                              |
| ------------ | -------------------------------------------------------- |
| `session`    | Store session ID silently (no visible change)            |
| `status`     | Light up next pipeline node, dim previous               |
| `retrieval`  | Show "Retrieved N docs" badge on `retrieve_docs` node   |
| `rerank`     | Show "Reranked to N" badge on `rerank_docs` node        |
| `token`      | Append character to streaming bubble in real time        |
| `sources`    | Render `SourcePanel` below the message                   |
| `[DONE]`     | Replace streaming buffer with markdown, hide cursor      |

---

## Component Hierarchy

```
ChatPage
└── ChatThread (organism)
    ├── MessageBubble[] (organism)
    │   ├── StreamingText (molecule) — live token display
    │   ├── MarkdownView (molecule) — post-stream rendered markdown
    │   ├── AgentPipeline (molecule) — node progress row
    │   └── SourcePanel (organism) — citations + issue badge
    └── ChatInput (molecule)
        └── SendButton (atom)
```

---

## AgentPipeline Component

Visualizes the 7-node LangGraph pipeline in real time.

```tsx
// src/molecules/AgentPipeline/AgentPipeline.tsx

const NODE_LABELS: Record<AgentNodeName, string> = {
  classify_question:  'Classify',
  rewrite_question:   'Rewrite',
  resolve_context:    'Context',
  retrieve_docs:      'Retrieve',
  rerank_docs:        'Rerank',
  generate_answer:    'Answer',
  classify_issue:     'Classify Issue',
};

interface AgentPipelineProps {
  nodeStatuses: Record<AgentNodeName, NodeStatus>;
  retrievedCount: number | null;
  rerankedCount: number | null;
  isCollapsed?: boolean;
}

export const AgentPipeline = memo(function AgentPipeline({
  nodeStatuses,
  retrievedCount,
  rerankedCount,
  isCollapsed = false,
}: AgentPipelineProps) {
  if (isCollapsed) return null;

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexWrap: 'wrap' }}>
      {AGENT_NODE_ORDER.map((node, i) => (
        <React.Fragment key={node}>
          <AgentNodeBadge
            label={NODE_LABELS[node]}
            status={nodeStatuses[node]}
            badge={
              node === 'retrieve_docs' && retrievedCount != null ? `${retrievedCount}` :
              node === 'rerank_docs'   && rerankedCount != null  ? `→${rerankedCount}` :
              undefined
            }
          />
          {i < AGENT_NODE_ORDER.length - 1 && (
            <Box component="span" sx={{ color: 'text.disabled', fontSize: 10 }}>›</Box>
          )}
        </React.Fragment>
      ))}
    </Box>
  );
});
```

### NodeStatus Visual Rules

```tsx
// src/molecules/AgentNodeBadge/AgentNodeBadge.tsx

const STATUS_STYLES: Record<NodeStatus, SxProps<Theme>> = {
  pending: { color: 'text.disabled', bgcolor: 'transparent' },
  active:  {
    color: 'primary.main',
    bgcolor: 'primary.50',
    animation: 'pulse 1.2s ease-in-out infinite',
    '@keyframes pulse': {
      '0%, 100%': { opacity: 1 },
      '50%': { opacity: 0.5 },
    },
  },
  done: { color: 'success.main', bgcolor: 'success.50' },
};
```

---

## StreamingText Component

Renders tokens in real time. On stream completion, hands off to `MarkdownView`.

```tsx
// src/molecules/StreamingText/StreamingText.tsx

interface StreamingTextProps {
  content: string;
  isStreaming: boolean;
}

export const StreamingText = memo(function StreamingText({
  content,
  isStreaming,
}: StreamingTextProps) {
  if (!isStreaming) {
    return <MarkdownView content={content} />;
  }

  return (
    <Box
      sx={{
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        fontFamily: 'inherit',
        lineHeight: 1.7,
      }}
    >
      {content}
      <StreamingCursor />
    </Box>
  );
});
```

### StreamingCursor Atom

```tsx
// src/atoms/StreamingCursor/StreamingCursor.tsx

export const StreamingCursor = memo(function StreamingCursor() {
  return (
    <Box
      component="span"
      sx={{
        display: 'inline-block',
        width: '2px',
        height: '1em',
        bgcolor: 'primary.main',
        ml: 0.25,
        verticalAlign: 'middle',
        animation: 'blink 1s step-end infinite',
        '@keyframes blink': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0 },
        },
      }}
    />
  );
});
```

---

## SourcePanel Component

Renders source citations and the issue classification after stream completes.

```tsx
// src/organisms/SourcePanel/SourcePanel.tsx

interface SourcePanelProps {
  sources: SourceDocument[];
  issueType: IssueType;
  issueConfidence: number | null;
  issueClassificationReason: string | null;
}

export const SourcePanel = memo(function SourcePanel({
  sources,
  issueType,
  issueConfidence,
  issueClassificationReason,
}: SourcePanelProps) {
  const [expanded, setExpanded] = useState(false);

  if (!sources.length && !issueType) return null;

  return (
    <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      {issueType && (
        <IssueClassBadge
          issueType={issueType}
          confidence={issueConfidence}
          reason={issueClassificationReason}
        />
      )}
      {sources.length > 0 && (
        <>
          <Typography variant="caption" color="text.secondary">
            {sources.length} source{sources.length > 1 ? 's' : ''}
          </Typography>
          {sources.map((source, i) => (
            <SourceCard key={i} source={source} />
          ))}
        </>
      )}
    </Box>
  );
});
```

---

## IssueClassBadge — Generative Classification Display

```tsx
// src/molecules/IssueClassBadge/IssueClassBadge.tsx

const ISSUE_COLOR: Record<string, 'error' | 'warning' | 'default'> = {
  bug: 'error',
  business_condition: 'warning',
  unknown: 'default',
};

interface IssueClassBadgeProps {
  issueType: IssueType;
  confidence: number | null;
  reason: string | null;
}

export const IssueClassBadge = memo(function IssueClassBadge({
  issueType,
  confidence,
  reason,
}: IssueClassBadgeProps) {
  const [showReason, setShowReason] = useState(false);
  if (!issueType) return null;

  const color = ISSUE_COLOR[issueType] ?? 'default';
  const label = issueType === 'business_condition' ? 'Business Condition' : issueType.toUpperCase();

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Chip
          label={label}
          color={color}
          size="small"
          sx={{ fontWeight: 600, textTransform: 'capitalize' }}
        />
        {confidence != null && (
          <Typography variant="caption" color="text.secondary">
            {Math.round(confidence * 100)}% confidence
          </Typography>
        )}
        {reason && (
          <IconButton size="small" onClick={() => setShowReason((v) => !v)}>
            <InfoOutlinedIcon fontSize="small" />
          </IconButton>
        )}
      </Box>
      {showReason && reason && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
          {reason}
        </Typography>
      )}
    </Box>
  );
});
```

---

## MessageBubble — Composing It All

```tsx
// src/organisms/MessageBubble/MessageBubble.tsx

interface MessageBubbleProps {
  message: Message;
  nodeStatuses?: Record<AgentNodeName, NodeStatus>;
  retrievedCount?: number | null;
  rerankedCount?: number | null;
  isPipelineCollapsed?: boolean;
}

export const MessageBubble = memo(function MessageBubble({
  message,
  nodeStatuses,
  retrievedCount,
  rerankedCount,
  isPipelineCollapsed,
}: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <Box sx={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', mb: 2 }}>
      <Box
        sx={{
          maxWidth: '75%',
          p: 2,
          borderRadius: (t) => t.shape.borderRadius * 1.5,
          bgcolor: isUser ? 'primary.main' : 'background.paper',
          color: isUser ? 'primary.contrastText' : 'text.primary',
          border: isUser ? 'none' : 1,
          borderColor: 'divider',
        }}
      >
        {!isUser && nodeStatuses && (
          <AgentPipeline
            nodeStatuses={nodeStatuses}
            retrievedCount={retrievedCount ?? null}
            rerankedCount={rerankedCount ?? null}
            isCollapsed={isPipelineCollapsed}
          />
        )}

        <StreamingText content={message.content} isStreaming={!!message.isStreaming} />

        {!message.isStreaming && message.sources && (
          <SourcePanel
            sources={message.sources}
            issueType={message.issueType ?? null}
            issueConfidence={message.issueConfidence ?? null}
            issueClassificationReason={message.issueClassificationReason ?? null}
          />
        )}
      </Box>
    </Box>
  );
});
```

---

## Generative UI Rules

1. **Never show a blank screen** during streaming — always have the pipeline visible as a minimum.
2. **Pipeline collapses after `[DONE]`** — default `isCollapsed = true` after finalization, expandable on click.
3. **SourcePanel only renders after `sources` event** — never during streaming.
4. **IssueClassBadge only renders when `issue_type` is not `null`** — check before rendering.
5. **Never re-render the entire `ChatThread`** on each token — use `memo()` + scoped state to isolate token appends to `StreamingText` only.
6. **Markdown renders only after `[DONE]`** — during streaming use raw `pre-wrap` text to avoid parser thrashing.

---

## Checklist

- [ ] `AgentPipeline` renders from first `status` event
- [ ] Each `status` event advances `active` node and marks previous as `done`
- [ ] `StreamingCursor` blinks during streaming, disappears on `[DONE]`
- [ ] `MarkdownView` only renders when `isStreaming === false`
- [ ] `SourcePanel` only renders when `sources` event received
- [ ] `IssueClassBadge` hidden when `issue_type === null`
- [ ] `AgentPipeline` collapsed by default after stream finishes
- [ ] `MessageBubble` wrapped in `memo()` — re-renders only when its own props change
- [ ] No full `ChatThread` re-render per token
