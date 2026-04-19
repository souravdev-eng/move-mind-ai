import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ToolCallBlock } from "./ToolCallBlock";

const TOOL_CALL = {
  name: "search_logs",
  server: "cms3-repo",
  input: '{"query": "step_4"}',
  output: '{"results": []}',
  latencyMs: 42,
};

describe("ToolCallBlock", () => {
  it("renders collapsed by default", () => {
    render(<ToolCallBlock toolCall={TOOL_CALL} />);
    expect(screen.getByText(/search_logs/)).toBeInTheDocument();
    expect(screen.queryByText(/step_4/)).not.toBeInTheDocument();
  });

  it("expands on toggle click to show input/output", () => {
    render(<ToolCallBlock toolCall={TOOL_CALL} />);
    fireEvent.click(screen.getByRole("button", { name: /expand tool call/i }));
    expect(screen.getByText(/step_4/)).toBeInTheDocument();
  });

  it("collapses again on second toggle click", () => {
    render(<ToolCallBlock toolCall={TOOL_CALL} />);
    const btn = screen.getByRole("button", { name: /expand tool call/i });
    fireEvent.click(btn);
    fireEvent.click(screen.getByRole("button", { name: /collapse tool call/i }));
    expect(screen.getByRole("button", { name: /expand tool call/i })).toBeInTheDocument();
  });
});
