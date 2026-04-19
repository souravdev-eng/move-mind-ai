import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("IngestionRunsPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/logs/runs");
    await waitFor(() => {
      expect(screen.getByText(/recent ingestion runs/i)).toBeInTheDocument();
    });
  });
});
