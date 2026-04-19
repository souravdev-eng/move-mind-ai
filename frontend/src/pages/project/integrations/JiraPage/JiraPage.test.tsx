import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("JiraPage", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/projects/cms3/integrations/jira");
    await waitFor(() => {
      expect(screen.getByText(/create tickets from investigations/i)).toBeInTheDocument();
    });
  });

  it("switches to mapping tab", async () => {
    renderAt("/orgs/acme/projects/cms3/integrations/jira");
    await waitFor(() => screen.getByRole("tab", { name: /mapping/i }));
    fireEvent.click(screen.getByRole("tab", { name: /mapping/i }));
    await waitFor(() => {
      expect(screen.getByText(/verdict → jira labels/i)).toBeInTheDocument();
    });
  });

  it("switches to activity tab and shows ticket table", async () => {
    renderAt("/orgs/acme/projects/cms3/integrations/jira");
    await waitFor(() => screen.getByRole("tab", { name: /activity/i }));
    fireEvent.click(screen.getByRole("tab", { name: /activity/i }));
    await waitFor(() => {
      expect(screen.getByRole("columnheader", { name: /key/i })).toBeInTheDocument();
    });
  });
});
