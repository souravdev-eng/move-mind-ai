import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

const BASE = "/orgs/acme/projects/cms3/code-context/mcp/mcp_cms3_repo";

describe("McpServerDetailPage", () => {
  it("renders without crash", async () => {
    renderAt(BASE);
    await waitFor(() => {
      expect(screen.getByText(/acme\/cms3 code server/i)).toBeInTheDocument();
    });
  });

  it("switches to resources tab", async () => {
    renderAt(BASE);
    await waitFor(() => screen.getByRole("tab", { name: /resources/i }));
    fireEvent.click(screen.getByRole("tab", { name: /resources/i }));
    await waitFor(() => {
      expect(screen.getByText(/last read/i)).toBeInTheDocument();
    });
  });

  it("switches to invocations tab", async () => {
    renderAt(BASE);
    await waitFor(() => screen.getByRole("tab", { name: /invocations/i }));
    fireEvent.click(screen.getByRole("tab", { name: /invocations/i }));
    await waitFor(() => {
      expect(screen.getByRole("columnheader", { name: /when/i })).toBeInTheDocument();
    });
  });

  it("switches to health tab", async () => {
    renderAt(BASE);
    await waitFor(() => screen.getByRole("tab", { name: /health/i }));
    fireEvent.click(screen.getByRole("tab", { name: /health/i }));
    await waitFor(() => {
      expect(screen.getByText(/last heartbeat/i)).toBeInTheDocument();
    });
  });
});
