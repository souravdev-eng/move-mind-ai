import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "./App";

describe("App", () => {
  beforeEach(() => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ok" }),
    } as Response);
  });

  it("renders the title", () => {
    render(<App />);
    expect(screen.getByText("Move Mind AI")).toBeInTheDocument();
  });
});
