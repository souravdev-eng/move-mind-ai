import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("JiraPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/integrations/jira");
    await waitFor(() => {
      expect(screen.getByText(/create tickets from investigations/i)).toBeInTheDocument();
    });
  });
});
