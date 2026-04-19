import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("ConversationsPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/conversations");
    await waitFor(() => {
      expect(screen.getAllByText(/conversations/i)[0]).toBeInTheDocument();
    });
  });
});
