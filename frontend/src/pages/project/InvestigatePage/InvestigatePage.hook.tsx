import { useState } from "react";

import { useActiveProject } from "@/hooks/useActiveProject";
import { useSimulatedStream } from "@/hooks/useSimulatedStream";
import { type ExplanationMode } from "@/interfaces/domain";
import { cannedEvidence } from "@/mocks";

export function useInvestigatePage() {
  const project = useActiveProject();
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<ExplanationMode>("manager");
  const [correlationKey, setCorrelationKey] = useState("");
  const [timeWindow, setTimeWindow] = useState("24h");
  const { messages, streaming, submit, reset } = useSimulatedStream();

  function onSubmit(e: { preventDefault: () => void }) {
    e.preventDefault();
    const q = input.trim();
    if (!q || streaming) {
      return;
    }
    submit(q);
    setInput("");
  }

  return {
    project,
    input,
    setInput,
    mode,
    setMode,
    correlationKey,
    setCorrelationKey,
    timeWindow,
    setTimeWindow,
    messages,
    streaming,
    reset,
    onSubmit,
    hasMessages: messages.length > 0,
    evidence: cannedEvidence,
  };
}
