---
trigger: model_decision
description: Testing guide for Move Mind AI — Vitest + RTL patterns, SSE ReadableStream mocks, chatReducer unit tests, streaming hook tests
---

# Testing Guide

## Philosophy

**Quality over quantity.** 10 tests that catch real bugs > 100 tests that test implementation details.

## What to Test (Priority)

| Priority     | Target                           | Why                                          |
| ------------ | -------------------------------- | -------------------------------------------- |
| **Critical** | `src/api/chatClient.ts`          | SSE parsing correctness, HTTP error handling |
| **Critical** | `src/utils/`                     | Pure functions, easy to test, high value     |
| **High**     | `useChat`, `useSSEStream`        | Streaming state machine logic                |
| **High**     | `chatReducer`                    | All `ChatAction` transitions                 |
| **Medium**   | `StreamingText`, `AgentPipeline` | Streaming → finalized state rendering        |
| **Low**      | Simple presentational atoms      | Only if conditional logic exists             |

## What NOT to Test

- MUI component internals (Button renders, Chip color)
- Simple UI that just renders props (use visual review instead)
- Constants (`const AGENT_NODE_ORDER = [...]`)
- The actual LangGraph backend (covered by backend tests)

## Testing Stack

```
Framework:     Vitest
Components:    React Testing Library
Hooks:         @testing-library/react → renderHook
API Mocking:   msw (Mock Service Worker)
```

## Patterns

### Utility Functions

```tsx
// utils/format.test.ts
describe("formatCurrency", () => {
  it("formats positive numbers correctly", () => {
    expect(formatCurrency(1234.56)).toBe("$1,234.56");
  });

  it("handles negative numbers", () => {
    expect(formatCurrency(-50)).toBe("-$50.00");
  });

  it("returns $0.00 for zero", () => {
    expect(formatCurrency(0)).toBe("$0.00");
  });

  it("handles undefined gracefully", () => {
    expect(formatCurrency(undefined)).toBe("$0.00");
  });
});
```

### Custom Hooks

```tsx
// hooks/useCounter.test.ts
import { renderHook, act } from "@testing-library/react";
import { useCounter } from "./useCounter";

describe("useCounter", () => {
  it("starts with initial value", () => {
    const { result } = renderHook(() => useCounter(5));
    expect(result.current.count).toBe(5);
  });

  it("increments correctly", () => {
    const { result } = renderHook(() => useCounter(0));

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });
});
```

### Components with User Interaction

```tsx
// organisms/SearchForm.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { SearchForm } from "./SearchForm";

describe("SearchForm", () => {
  it("calls onSearch when form is submitted", () => {
    const onSearch = vi.fn();
    render(<SearchForm onSearch={onSearch} />);

    fireEvent.change(screen.getByRole("textbox"), {
      target: { value: "test query" },
    });
    fireEvent.click(screen.getByRole("button", { name: /search/i }));

    expect(onSearch).toHaveBeenCalledWith("test query");
  });

  it("disables button when input is empty", () => {
    render(<SearchForm onSearch={vi.fn()} />);

    expect(screen.getByRole("button", { name: /search/i })).toBeDisabled();
  });
});
```

## Test Naming

```tsx
// ✅ Good - describes behavior
it("should format currency correctly for negative numbers");
it("returns empty array when no items match filter");
it("calls onSubmit with form data when valid");

// ❌ Bad - vague
it("test format");
it("works correctly");
it("handles edge case");
```

## AAA Pattern

```tsx
it("filters items by status", () => {
  // Arrange
  const items = [
    { id: "1", status: "active" },
    { id: "2", status: "inactive" },
  ];

  // Act
  const result = filterByStatus(items, "active");

  // Assert
  expect(result).toHaveLength(1);
  expect(result[0].id).toBe("1");
});
```

## Anti-Patterns

```tsx
// ❌ Testing implementation details
expect(wrapper.state("isOpen")).toBe(true);

// ✅ Test behavior
expect(screen.getByRole("dialog")).toBeVisible();

// ❌ Arbitrary waits
await new Promise((resolve) => setTimeout(resolve, 1000));

// ✅ Use proper async utilities
await waitFor(() => expect(screen.getByText("Loaded")).toBeVisible());

// ❌ Complex logic in tests
const expected = items.filter((i) => i.active).map((i) => i.id);

// ✅ Simple, explicit assertions
expect(result).toEqual(["id1", "id2"]);
```

## SSE Streaming Tests

```tsx
// src/api/chatClient.test.ts
import { describe, it, expect, vi } from "vitest";
import { streamChat } from "./chatClient";

function mockSSEResponse(lines: string[]) {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      for (const line of lines) {
        controller.enqueue(encoder.encode(line + "\n"));
      }
      controller.close();
    },
  });
  return new Response(stream, { status: 200 });
}

describe("streamChat", () => {
  it("calls onSession when session event received", async () => {
    global.fetch = vi
      .fn()
      .mockResolvedValue(
        mockSSEResponse(['data: {"type":"session","session_id":"abc-123"}', "data: [DONE]"])
      );

    const onSession = vi.fn();
    await streamChat("test question", null, {
      onSession,
      onNodeStart: vi.fn(),
      onToken: vi.fn(),
      onSources: vi.fn(),
      onDone: vi.fn(),
      onError: vi.fn(),
      onRetrieval: vi.fn(),
      onRerank: vi.fn(),
    });

    expect(onSession).toHaveBeenCalledWith("abc-123");
  });

  it("calls onToken for each token event", async () => {
    global.fetch = vi
      .fn()
      .mockResolvedValue(
        mockSSEResponse([
          'data: {"type":"token","content":"Hello"}',
          'data: {"type":"token","content":" world"}',
          "data: [DONE]",
        ])
      );

    const onToken = vi.fn();
    await streamChat("test", null, {
      onToken,
      onSession: vi.fn(),
      onNodeStart: vi.fn(),
      onSources: vi.fn(),
      onDone: vi.fn(),
      onError: vi.fn(),
      onRetrieval: vi.fn(),
      onRerank: vi.fn(),
    });

    expect(onToken).toHaveBeenCalledTimes(2);
    expect(onToken).toHaveBeenNthCalledWith(1, "Hello");
    expect(onToken).toHaveBeenNthCalledWith(2, " world");
  });

  it("calls onDone on [DONE] sentinel", async () => {
    global.fetch = vi.fn().mockResolvedValue(mockSSEResponse(["data: [DONE]"]));
    const onDone = vi.fn();
    await streamChat("test", null, {
      onDone,
      onSession: vi.fn(),
      onNodeStart: vi.fn(),
      onToken: vi.fn(),
      onSources: vi.fn(),
      onError: vi.fn(),
      onRetrieval: vi.fn(),
      onRerank: vi.fn(),
    });
    expect(onDone).toHaveBeenCalledOnce();
  });
});
```

## chatReducer Tests

```tsx
// src/context/ChatContext.test.ts
import { describe, it, expect } from "vitest";
import { chatReducer, initialState } from "./ChatContext";

describe("chatReducer", () => {
  it("adds user message with isLoading true", () => {
    const next = chatReducer(initialState, { type: "ADD_USER_MESSAGE", content: "Hello" });
    expect(next.messages).toHaveLength(1);
    expect(next.messages[0].role).toBe("user");
    expect(next.isLoading).toBe(true);
  });

  it("appends token to correct message", () => {
    const withMsg = chatReducer(initialState, { type: "ADD_ASSISTANT_MESSAGE", id: "msg-1" });
    const withToken = chatReducer(withMsg, { type: "APPEND_TOKEN", id: "msg-1", token: "Hi" });
    expect(withToken.messages[0].content).toBe("Hi");
  });

  it("finalizes message with sources and clears isLoading", () => {
    const withMsg = chatReducer(initialState, { type: "ADD_ASSISTANT_MESSAGE", id: "msg-1" });
    const finalized = chatReducer(withMsg, {
      type: "FINALIZE_MESSAGE",
      id: "msg-1",
      sources: [],
      issueType: "bug",
      issueConfidence: 0.9,
    });
    expect(finalized.isLoading).toBe(false);
    expect(finalized.messages[0].isStreaming).toBe(false);
    expect(finalized.messages[0].issueType).toBe("bug");
  });
});
```

## Checklist

- [ ] Tests describe behavior, not implementation
- [ ] AAA pattern followed (Arrange, Act, Assert)
- [ ] No arbitrary sleeps/timeouts
- [ ] `chatClient` SSE parsing tested with mocked `ReadableStream`
- [ ] `chatReducer` all action types covered
- [ ] `useChat` / `useSSEStream` hook state transitions tested
- [ ] Mocks are minimal and focused
- [ ] Edge cases covered: empty sources, null issueType, network error
- [ ] Test names are descriptive
