import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("AppShell", () => {
  it("renders left rail with org nav section and project nav items", async () => {
    renderAt("/orgs/acme/dashboard");
    await waitFor(() => {
      expect(screen.getByText("Organisation")).toBeInTheDocument();
    });
    expect(screen.getAllByText(/investigate/i)[0]).toBeInTheDocument();
  });
});
