import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("OnboardingWizard", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/onboarding");
    await waitFor(() => {
      expect(screen.getByText(/create project/i)).toBeInTheDocument();
    });
  });
});
