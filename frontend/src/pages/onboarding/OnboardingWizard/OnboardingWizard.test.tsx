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

  it("navigates back from step 1 to step 0", async () => {
    renderAt("/orgs/acme/onboarding");
    const nextBtn = await screen.findByRole("button", { name: /next/i });
    fireEvent.click(nextBtn);
    await waitFor(() => {
      expect(screen.getByText(/choose a log source/i)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /back/i }));
    await waitFor(() => {
      expect(screen.getByLabelText(/project name/i)).toBeInTheDocument();
    });
  });

  it("shows connector cards on step 1", async () => {
    renderAt("/orgs/acme/onboarding");
    const nextBtn = await screen.findByRole("button", { name: /next/i });
    fireEvent.click(nextBtn);
    await waitFor(() => {
      expect(screen.getByText("Amazon S3")).toBeInTheDocument();
      expect(screen.getByText("File upload")).toBeInTheDocument();
      expect(screen.getByText("Webhook")).toBeInTheDocument();
    });
  });

  it("shows configure step on step 2", async () => {
    renderAt("/orgs/acme/onboarding");
    const nextBtn = await screen.findByRole("button", { name: /next/i });
    fireEvent.click(nextBtn);
    fireEvent.click(nextBtn);
    await waitFor(() => {
      expect(screen.getByLabelText(/bucket/i)).toBeInTheDocument();
      expect(screen.getByText(/test connection/i)).toBeInTheDocument();
    });
  });

  it("shows pull sample step on step 3", async () => {
    renderAt("/orgs/acme/onboarding");
    const nextBtn = await screen.findByRole("button", { name: /next/i });
    fireEvent.click(nextBtn);
    fireEvent.click(nextBtn);
    fireEvent.click(nextBtn);
    await waitFor(() => {
      expect(screen.getByText(/pulling sample/i)).toBeInTheDocument();
    });
  });

  it("shows profiler review on step 4", async () => {
    renderAt("/orgs/acme/onboarding");
    for (let i = 0; i < 4; i++) {
      const btn = screen.getByRole("button", { name: /next/i });
      fireEvent.click(btn);
    }
    await waitFor(() => {
      expect(screen.getByText(/confidence indicators/i)).toBeInTheDocument();
    });
  });

  it("shows confirm & ingest on step 5 with kick off button", async () => {
    renderAt("/orgs/acme/onboarding");
    for (let i = 0; i < 5; i++) {
      const btn = screen.getByRole("button", { name: /next/i });
      fireEvent.click(btn);
    }
    await waitFor(() => {
      expect(screen.getAllByText(/kick off ingestion/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/close this tab/i)).toBeInTheDocument();
    });
  });

  it("shows ready screen on step 6 with start investigating button", async () => {
    renderAt("/orgs/acme/onboarding");
    for (let i = 0; i < 5; i++) {
      const btn = screen.getByRole("button", { name: /next/i });
      fireEvent.click(btn);
    }
    const kickOff = screen.getByRole("button", { name: /kick off ingestion/i });
    fireEvent.click(kickOff);
    await waitFor(() => {
      expect(screen.getByText(/you're live/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /start investigating/i })).toBeInTheDocument();
    });
  });
});
