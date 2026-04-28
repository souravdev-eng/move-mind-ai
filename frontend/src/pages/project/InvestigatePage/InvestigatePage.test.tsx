import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { renderAt } from "@/test/renderApp";

// Mock useChatStream so we can control its return values without hitting the network
const mockSubmit = vi.fn();
const mockReset = vi.fn();
const mockCancel = vi.fn();

vi.mock("@/hooks/useChatStream", () => ({
  useChatStream: () => ({
    messages: [],
    streaming: false,
    error: null,
    sessionId: null,
    pipeline: [],
    sources: [],
    issueType: null,
    issueConfidence: null,
    issueReason: null,
    submit: mockSubmit,
    reset: mockReset,
    cancel: mockCancel,
    hasMessages: false,
  }),
}));

describe("InvestigatePage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/investigate");
    await waitFor(() => {
      expect(screen.getAllByText(/investigate/i)[0]).toBeInTheDocument();
    });
  });

  it("shows suggested questions when no messages", async () => {
    renderAt("/orgs/acme/projects/cms3/investigate");
    await waitFor(() => {
      expect(screen.getByText(/suggested questions/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/CID 7093495/)).toBeInTheDocument();
  });

  it("fills input on suggestion click", async () => {
    renderAt("/orgs/acme/projects/cms3/investigate");
    const suggestion = await screen.findByText(/CID 7093495/);
    await userEvent.click(suggestion);
    const input = screen.getByLabelText(/question input/i);
    expect(input).toHaveValue("Why is CID 7093495 stuck on step 4?");
  });

  it("send button is disabled when input is empty", async () => {
    renderAt("/orgs/acme/projects/cms3/investigate");
    await waitFor(() => {
      expect(screen.getByLabelText(/send/i)).toBeDisabled();
    });
  });

  it("renders scope panel", async () => {
    renderAt("/orgs/acme/projects/cms3/investigate");
    await waitFor(() => {
      expect(screen.getByText(/scope/i)).toBeInTheDocument();
    });
  });
});
