import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("ComingSoonPage", () => {
  it("renders without crash for a stub route", async () => {
    renderAt("/orgs/acme/projects/cms3/evaluations");
    await waitFor(() => {
      expect(screen.getByText(/coming soon/i)).toBeInTheDocument();
    });
  });
});
