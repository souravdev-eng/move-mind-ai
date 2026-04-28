import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("SettingsPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/settings");
    await waitFor(() => {
      expect(screen.getByText(/project settings/i)).toBeInTheDocument();
    });
  });
});
