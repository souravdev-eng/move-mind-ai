import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("OverviewPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/overview");
    await waitFor(() => {
      expect(screen.getAllByText("CMS3")[0]).toBeInTheDocument();
    });
  });
});
