import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { type ChatMessage } from "@/interfaces/domain";

import { MessageList } from "./MessageList";

const MESSAGES: ChatMessage[] = [
  {
    id: "1",
    role: "user",
    content: "Why is step 4 failing?",
    createdAtIso: "2024-01-01T00:00:00Z",
  },
  {
    id: "2",
    role: "tool",
    content: "The failure is caused by a timeout.",
    createdAtIso: "2024-01-01T00:00:01Z",
    toolCall: {
      name: "search_logs",
      server: "cms3-repo",
      input: '{"q":"step_4"}',
      output: '{"hits":1}',
      latencyMs: 38,
    },
  },
];

describe("MessageList", () => {
  it("renders user and assistant messages", () => {
    render(<MessageList messages={MESSAGES} streaming={false} />);
    expect(screen.getByText(/why is step 4 failing/i)).toBeInTheDocument();
    expect(screen.getByText(/caused by a timeout/i)).toBeInTheDocument();
  });

  it("renders ToolCallBlock for tool-role messages", () => {
    render(<MessageList messages={MESSAGES} streaming={false} />);
    expect(screen.getByRole("button", { name: /expand tool call/i })).toBeInTheDocument();
  });

  it("renders pipeline nodes when provided", () => {
    const pipeline = [{ name: "retrieve_docs" as const, status: "running" as const }];
    const userOnly: ChatMessage[] = [MESSAGES[0]!];
    render(<MessageList messages={userOnly} streaming pipeline={pipeline} />);
    expect(screen.getAllByText(/retrieving/i).length).toBeGreaterThan(0);
  });
});
