import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderAt } from "@/test/renderApp";

describe("OnboardingWizard", () => {
  it("renders without crash", async () => {
    renderAt("/orgs/acme/onboarding");
    await waitFor(() => {
      expect(screen.getByText(/create project/i)).toBeInTheDocument();
    });
  });

  it("advances to next step on Next click", async () => {
    renderAt("/orgs/acme/onboarding");
    const nextBtn = await screen.findByRole("button", { name: /next/i });
    fireEvent.click(nextBtn);
    await waitFor(() => {
      expect(screen.getByText(/connect log source/i)).toBeInTheDocument();
    });
  });

  it("back button is disabled on step 0", async () => {
    renderAt("/orgs/acme/onboarding");
    const backBtn = await screen.findByRole("button", { name: /back/i });
    expect(backBtn).toBeDisabled();
  });

  it("back button is enabled after advancing", async () => {
    renderAt("/orgs/acme/onboarding");
    const nextBtn = await screen.findByRole("button", { name: /next/i });
    fireEvent.click(nextBtn);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /back/i })).not.toBeDisabled();
    });
  });
});
