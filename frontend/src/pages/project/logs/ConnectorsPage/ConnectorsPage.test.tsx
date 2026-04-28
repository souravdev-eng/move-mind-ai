import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("ConnectorsPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/logs/connectors");
    await waitFor(() => {
      expect(screen.getByText(/configured log sources/i)).toBeInTheDocument();
    });
  });
});
