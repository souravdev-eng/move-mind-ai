import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("DashboardPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/dashboard");
    await waitFor(() => {
      expect(screen.getByText(/organisation dashboard/i)).toBeInTheDocument();
    });
  });
});
