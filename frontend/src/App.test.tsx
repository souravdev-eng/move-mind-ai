import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  it("mounts the router and lands on the org dashboard", async () => {
    window.history.pushState({}, "", "/");
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Organisation dashboard/i)).toBeInTheDocument();
    });
  });
});
