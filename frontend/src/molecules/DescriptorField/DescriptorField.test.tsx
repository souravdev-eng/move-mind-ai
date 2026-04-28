import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { type DescriptorFieldValue } from "@/interfaces/domain";

import { DescriptorField } from "./DescriptorField";

const FIELD: DescriptorFieldValue = {
  value: "payment-svc",
  confidence: "high",
  source: "profiler",
  editedByUser: false,
};

describe("DescriptorField", () => {
  it("renders label and field value", () => {
    render(<DescriptorField label="service" field={FIELD} />);
    expect(screen.getByText("service")).toBeInTheDocument();
    expect(screen.getByDisplayValue("payment-svc")).toBeInTheDocument();
  });

  it("is read-only when readOnly=true", () => {
    render(<DescriptorField label="env" field={{ ...FIELD, value: "prod" }} readOnly />);
    const input = screen.getByDisplayValue("prod");
    expect(input).toBeInTheDocument();
  });
});
