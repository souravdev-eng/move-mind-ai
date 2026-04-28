---
trigger: model_decision
description: Structured logging guide — createLogger patterns for chatService, streamHandler, agentPipeline, chatContext modules. Log levels and what to log in SSE streaming hooks.
---

# Observability Guide

## Overview

This project uses a structured logging system (`src/utils/logger.ts`) for debugging and monitoring. This guide covers when and how to log effectively.

## Logger Setup

### Using Pre-configured Loggers

```tsx
import { loggers } from "../../utils/logger";

// Use existing loggers for known modules
const log = loggers.chatService; // chatClient.ts — API calls
const log = loggers.streamHandler; // useSSEStream — SSE event parsing
const log = loggers.agentPipeline; // useAgentPipeline — node state updates
const log = loggers.chatContext; // ChatContext reducer
```

### Creating New Loggers

```tsx
import { createLogger } from "../../utils/logger";

// Create for new component/module
const log = createLogger("SourcePanel");

// Create function-specific logger
const functionLog = log.forFunction("handleSend");

// Add metadata context
const contextLog = log.withMetadata({ sessionId: "123", messageId: "msg-abc" });
```

## Log Levels

| Level   | When to Use             | Example                            |
| ------- | ----------------------- | ---------------------------------- |
| `debug` | Detailed debugging info | State changes, function entry/exit |
| `info`  | General flow info       | API calls, user actions            |
| `warn`  | Recoverable issues      | Fallback used, deprecated feature  |
| `error` | Failures                | API errors, exceptions             |

## What to Log

### DO Log

```tsx
// API operations
log.apiStart("fetchJourney", { journeyId });
log.apiSuccess("fetchJourney", { pageCount: data.pages.length });
log.apiError("fetchJourney", error, { journeyId });

// User actions
log.info("User saved journey", { journeyId, pageCount });

// State changes (important ones)
log.stateChange("selectedNode", oldId, newId);

// Errors with context
log.error("Failed to parse journey data", error, { rawData });

// Warnings for degraded behavior
log.warn("Using cached data - network unavailable", { cacheAge: "5m" });
```

### DON'T Log

```tsx
// ❌ Sensitive data
log.info('User logged in', { password: '...' });

// ❌ High-frequency events (floods console)
onMouseMove={(e) => log.debug('Mouse moved', { x: e.x })}

// ❌ Redundant logs
log.info('Starting function');
log.info('Function started');
log.info('Now in function');

// ❌ Raw objects without context
log.info(data); // What is this?
```

## Patterns

### API/Service Layer

```tsx
// src/api/chatClient.ts
import { loggers } from '../utils/logger';

const log = loggers.chatService;

export async function streamChat(
  message: string,
  sessionId: string | null,
  callbacks: ChatStreamCallbacks
): Promise<void> {
  const fn = log.forFunction('streamChat');
  fn.apiStart('streamChat', { sessionId, messageLength: message.length });

  try {
    const response = await fetch('/api/v1/chat', { ... });
    fn.apiSuccess('streamChat', { status: response.status });
    // ... stream consumption
  } catch (error) {
    fn.apiError('streamChat', error, { sessionId });
    throw error;
  }
}
```

### Hooks

```tsx
// src/hooks/useSSEStream.ts
import { loggers } from "../utils/logger";

const log = loggers.streamHandler;

export function useSSEStream() {
  const fn = log.forFunction("useSSEStream");

  const handleEvent = (event: SSEEvent) => {
    fn.debug("SSE event received", { type: event.type });

    if (event.type === "status") {
      fn.info("Agent node started", { node: event.node });
    }
    if (event.type === "sources") {
      fn.info("Sources received", {
        count: event.sources.length,
        issueType: event.issue_type,
      });
    }
  };
}
```

### Context Reducers

```tsx
// src/context/ChatContext.tsx
import { loggers } from "../utils/logger";

const log = loggers.chatContext;

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  log.debug("Chat action dispatched", { type: action.type });

  switch (action.type) {
    case "FINALIZE_MESSAGE":
      log.info("Message finalized", { id: action.id, sourceCount: action.sources.length });
    // ...
  }
}
```

## Production Debugging

### Enable Debug Mode

In browser console:

```js
// Enable all logs
enableDebugMode(); // Then refresh

// Set specific level
setLogLevel("debug"); // or 'info', 'warn', 'error'

// Disable
disableDebugMode();
```

Or via URL:

```
https://app.example.com/editor?debug=true
```

### Reading Logs

Logs are structured for easy filtering:

```
[2024-01-15T10:30:45.123Z] [INFO] [JourneyService] [fetchJourney] API Call Started: fetchJourney
  Metadata: { id: 'journey-123' }
```

Filter in DevTools:

- By level: `[ERROR]`, `[WARN]`
- By component: `[JourneyService]`
- By function: `[fetchJourney]`

## Error Tracking

### Structured Error Logging

```tsx
try {
  await riskyOperation();
} catch (error) {
  // Log with full context
  log.error("Operation failed", error, {
    operation: "riskyOperation",
    userId: currentUser.id,
    journeyId,
    attemptNumber: retryCount,
  });

  // Show user-friendly message
  showNotification("Something went wrong. Please try again.");
}
```

### Error Boundaries

```tsx
// Page-level error boundary logs automatically
class PageErrorBoundary extends Component {
  componentDidCatch(error: Error, info: ErrorInfo) {
    const log = createLogger("ErrorBoundary");
    log.error("Uncaught error in component tree", error, {
      componentStack: info.componentStack,
    });
  }
}
```

## Adding New Module Logger

When creating a new service/page:

1. Add to `src/utils/logger.ts`:

```tsx
export const loggers = {
  chatService: createLogger("ChatService"),
  streamHandler: createLogger("StreamHandler"),
  agentPipeline: createLogger("AgentPipeline"),
  chatContext: createLogger("ChatContext"),
  // add new module:
  sourcePanel: createLogger("SourcePanel"),
};
```

2. Import and use:

```tsx
import { loggers } from "../../utils/logger";
const log = loggers.sourcePanel;
```

## Checklist

- [ ] Use structured logger, not raw `console.log`
- [ ] Log API start, success, and error
- [ ] Include context (IDs, counts, states)
- [ ] Never log sensitive data (passwords, tokens)
- [ ] Use appropriate log level
- [ ] Add new modules to `loggers` export
- [ ] Error logs include the error object and context
