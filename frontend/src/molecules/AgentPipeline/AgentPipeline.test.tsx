import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { type PipelineNode } from "@/hooks/useChatStream";

import { AgentPipeline } from "./AgentPipeline";

const runningPipeline: PipelineNode[] = [
  { name: "classify_question", status: "done" },
  { name: "rewrite_question", status: "done" },
  { name: "retrieve_docs", status: "running" },
];

const completedPipeline: PipelineNode[] = [
  { name: "classify_question", status: "done" },
  { name: "rewrite_question", status: "done" },
  { name: "retrieve_docs", status: "done" },
  { name: "rerank_docs", status: "done" },
  { name: "generate_answer", status: "done" },
];

describe("AgentPipeline", () => {
  it("returns null when nodes are empty", () => {
    const { container } = render(<AgentPipeline nodes={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("shows running indicator with active node label", () => {
    render(<AgentPipeline nodes={runningPipeline} />);
    expect(screen.getAllByText(/retrieving/i).length).toBeGreaterThan(0);
    expect(screen.getByText("(2/3)")).toBeInTheDocument();
  });

  it("shows individual step rows for running pipeline", () => {
    render(<AgentPipeline nodes={runningPipeline} />);
    expect(screen.getAllByText(/classifying/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/rewriting/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/retrieving/i).length).toBeGreaterThan(0);
  });

  it("shows collapsed summary when all done", () => {
    render(<AgentPipeline nodes={completedPipeline} />);
    expect(screen.getByText(/5 steps completed/i)).toBeInTheDocument();
  });

  it("expands completed pipeline on click", async () => {
    render(<AgentPipeline nodes={completedPipeline} />);
    const summary = screen.getByText(/5 steps completed/i);
    await userEvent.click(summary);
    expect(screen.getAllByText(/classifying/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/generating/i).length).toBeGreaterThan(0);
  });

  it("collapses expanded pipeline on second click", async () => {
    render(<AgentPipeline nodes={completedPipeline} />);
    // expand
    await userEvent.click(screen.getByText(/5 steps completed/i));
    expect(screen.getByText(/generating/i)).toBeInTheDocument();
    // collapse
    await userEvent.click(screen.getByText(/5 steps completed/i));
    // summary still visible
    expect(screen.getByText(/5 steps completed/i)).toBeInTheDocument();
  });

  it("falls back to node name when label is not in NODE_LABELS", () => {
    const custom: PipelineNode[] = [
      { name: "classify_question", status: "done" },
      { name: "unknown_node" as PipelineNode["name"], status: "running" },
    ];
    render(<AgentPipeline nodes={custom} />);
    expect(screen.getByText("unknown_node")).toBeInTheDocument();
  });
});
