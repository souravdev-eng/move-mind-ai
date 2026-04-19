import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

describe("App", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders the title and shows the healthy backend chip", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: "ok" }),
    } as Response);

    render(<App />);

    expect(screen.getByText("Move Mind AI")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Backend: ok")).toBeInTheDocument();
    });
  });

  it("shows error chip when the health endpoint returns non-2xx", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ status: "bad" }),
    } as Response);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Backend: error")).toBeInTheDocument();
    });
  });

  it("shows error chip when fetch rejects", async () => {
    vi.spyOn(global, "fetch").mockRejectedValue(new Error("network down"));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Backend: error")).toBeInTheDocument();
    });
  });

  it("toggles color mode via the toggle button and persists to localStorage", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: "ok" }),
    } as Response);

    const user = userEvent.setup();
    render(<App />);

    const toggle = screen.getByRole("button", { name: /switch to (light|dark) mode/i });
    const initialLabel = toggle.getAttribute("aria-label");
    await user.click(toggle);

    await waitFor(() => {
      const nextLabel = screen
        .getByRole("button", { name: /switch to (light|dark) mode/i })
        .getAttribute("aria-label");
      expect(nextLabel).not.toBe(initialLabel);
    });

    expect(localStorage.getItem("move-mind.color-mode")).toMatch(/^(light|dark)$/);
  });
});
