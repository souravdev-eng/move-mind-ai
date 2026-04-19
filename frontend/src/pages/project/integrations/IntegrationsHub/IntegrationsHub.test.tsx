import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("IntegrationsHub", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/integrations");
    await waitFor(() => {
      expect(
        screen.getByText(/connect movemind to your ticketing/i),
      ).toBeInTheDocument();
    });
  });
});
