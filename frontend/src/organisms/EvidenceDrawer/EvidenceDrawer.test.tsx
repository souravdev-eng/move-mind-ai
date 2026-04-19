import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { cannedEvidence } from "@/mocks";

import { EvidenceDrawer } from "./EvidenceDrawer";

describe("EvidenceDrawer", () => {
  it("renders evidence items from fixtures", () => {
    render(<EvidenceDrawer items={cannedEvidence} />);
    expect(screen.getByText(/evidence/i)).toBeInTheDocument();
    expect(screen.getAllByRole("heading", { level: 6 }).length).toBeGreaterThan(0);
  });

  it("renders placeholder when no items", () => {
    render(<EvidenceDrawer items={[]} />);
    expect(screen.getByText(/evidence will appear here/i)).toBeInTheDocument();
  });
});
