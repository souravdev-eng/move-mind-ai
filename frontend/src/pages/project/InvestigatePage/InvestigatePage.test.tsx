import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("InvestigatePage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/investigate");
    await waitFor(() => {
      expect(screen.getAllByText(/investigate/i)[0]).toBeInTheDocument();
    });
  });
});
