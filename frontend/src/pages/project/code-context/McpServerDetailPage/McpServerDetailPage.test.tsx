import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("McpServerDetailPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/code-context/mcp/mcp_cms3_repo");
    await waitFor(() => {
      expect(screen.getByText(/acme\/cms3 code server/i)).toBeInTheDocument();
    });
  });
});
