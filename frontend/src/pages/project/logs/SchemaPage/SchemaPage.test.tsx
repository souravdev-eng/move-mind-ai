import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("SchemaPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/logs/schema");
    await waitFor(() => {
      expect(screen.getAllByText(/schema & descriptor/i)[0]).toBeInTheDocument();
    });
  });
});
