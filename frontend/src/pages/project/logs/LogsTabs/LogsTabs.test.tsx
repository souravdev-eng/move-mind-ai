import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("LogsTabs navigation", () => {
  it("renders the logs tabs on ConnectorsPage", async () => {
    renderAt("/orgs/acme/projects/cms3/logs/connectors");
    await waitFor(() => screen.getByRole("tab", { name: /ingestion runs/i }));
    fireEvent.click(screen.getByRole("tab", { name: /ingestion runs/i }));
    await waitFor(() => {
      expect(screen.getByRole("tab", { name: /ingestion runs/i })).toBeInTheDocument();
    });
  });
});
