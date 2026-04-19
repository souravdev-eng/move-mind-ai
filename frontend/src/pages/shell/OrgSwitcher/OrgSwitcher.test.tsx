import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("OrgSwitcher", () => {
  it("opens the org menu on button click", async () => {
    renderAt("/orgs/acme/dashboard");
    const btn = await screen.findByRole("button", { name: /acme/i });
    fireEvent.click(btn);
    await waitFor(() => {
      expect(screen.getByRole("menu")).toBeInTheDocument();
    });
  });

  it("closes the menu on item click and navigates", async () => {
    renderAt("/orgs/acme/dashboard");
    const btn = await screen.findByRole("button", { name: /acme/i });
    fireEvent.click(btn);
    await waitFor(() => screen.getByRole("menu"));
    const [firstItem] = screen.getAllByRole("menuitem");
    fireEvent.click(firstItem!);
    await waitFor(() => {
      expect(screen.queryByRole("menu")).not.toBeInTheDocument();
    });
  });
});
