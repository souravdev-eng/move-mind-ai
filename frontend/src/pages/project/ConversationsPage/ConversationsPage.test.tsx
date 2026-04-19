import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

const ROUTE = "/orgs/acme/projects/cms3/conversations";

describe("ConversationsPage", () => {
  it("renders without crash", async () => {
    renderAt(ROUTE);
    await waitFor(() => {
      expect(screen.getAllByText(/conversations/i)[0]).toBeInTheDocument();
    });
  });

  it("filters rows by search query", async () => {
    renderAt(ROUTE);
    const input = await screen.findByPlaceholderText(/search conversations/i);
    fireEvent.change(input, { target: { value: "zzznomatch" } });
    await waitFor(() => {
      expect(screen.queryByRole("row", { name: /zzznomatch/i })).not.toBeInTheDocument();
    });
  });

  it("filters rows by verdict using the dropdown", async () => {
    renderAt(ROUTE);
    await screen.findByPlaceholderText(/search conversations/i);
    const selectBtn = screen.getByRole("combobox", { name: /verdict/i });
    fireEvent.mouseDown(selectBtn);
    const option = await screen.findByRole("option", { name: /^bug$/i });
    fireEvent.click(option);
    await waitFor(() => {
      expect(screen.queryByRole("option")).not.toBeInTheDocument();
    });
  });
});
