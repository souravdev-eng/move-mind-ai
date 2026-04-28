import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { type SourceDocumentDTO } from "@/interfaces/domain";

import { EvidenceDrawer } from "./EvidenceDrawer";

const mockSource: SourceDocumentDTO = {
  content: "step_order=4 level=error error_code=E_COND_NULL",
  chunk_type: "event",
  customer_id: "7093495",
  execution_id: "exec_5521",
  journey_id: "j_100",
  page_path: "/onboard/confirm",
  action: "evaluate_ui_condition",
  step_order: 4,
  target: "",
  decision_result: null,
  status: "failed",
  error_code: "E_COND_NULL",
};

describe("EvidenceDrawer", () => {
  it("renders summary chips for source documents", () => {
    render(<EvidenceDrawer sources={[mockSource]} />);
    expect(screen.getByText(/evidence/i)).toBeInTheDocument();
    expect(screen.getByText("event")).toBeInTheDocument();
    expect(screen.getByText("failed")).toBeInTheDocument();
  });

  it("expands card to show content on click", async () => {
    render(<EvidenceDrawer sources={[mockSource]} />);
    const expandBtn = screen.getByRole("button");
    await userEvent.click(expandBtn);
    expect(screen.getByText(/E_COND_NULL/)).toBeInTheDocument();
    expect(screen.getByText(/CID: 7093495/)).toBeInTheDocument();
  });

  it("renders placeholder when no sources", () => {
    render(<EvidenceDrawer sources={[]} />);
    expect(screen.getByText(/evidence will appear here/i)).toBeInTheDocument();
  });
});
