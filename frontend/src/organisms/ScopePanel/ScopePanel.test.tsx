import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ScopePanel } from "./ScopePanel";

const DEFAULT_PROPS = {
  mode: "manager" as const,
  onModeChange: vi.fn(),
  correlationKey: "",
  onCorrelationKeyChange: vi.fn(),
  timeWindow: "24h",
  onTimeWindowChange: vi.fn(),
};

describe("ScopePanel", () => {
  it("renders mode selector", () => {
    render(<ScopePanel {...DEFAULT_PROPS} />);
    expect(screen.getByText(/^mode$/i)).toBeInTheDocument();
  });

  it("calls onCorrelationKeyChange when input changes", () => {
    const onCorrelationKeyChange = vi.fn();
    render(<ScopePanel {...DEFAULT_PROPS} onCorrelationKeyChange={onCorrelationKeyChange} />);
    const input = screen.getByLabelText(/correlation/i);
    fireEvent.change(input, { target: { value: "CID-1234" } });
    expect(onCorrelationKeyChange).toHaveBeenCalledWith("CID-1234");
  });

  it("calls onModeChange when a mode button is clicked", () => {
    const onModeChange = vi.fn();
    render(<ScopePanel {...DEFAULT_PROPS} onModeChange={onModeChange} />);
    fireEvent.click(screen.getByRole("button", { name: /developer/i }));
    expect(onModeChange).toHaveBeenCalledWith("developer");
  });
});
