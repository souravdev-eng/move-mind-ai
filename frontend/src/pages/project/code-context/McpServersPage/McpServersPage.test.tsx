import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("McpServersPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/code-context/mcp");
    await waitFor(() => {
      expect(screen.getAllByText(/code context/i)[0]).toBeInTheDocument();
    });
  });
});
