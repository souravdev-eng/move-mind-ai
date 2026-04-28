import { useState } from "react";

import { useActiveProject } from "@/hooks/useActiveProject";
import { useChatStream } from "@/hooks/useChatStream";
import { type ExplanationMode } from "@/interfaces/domain";

export function useInvestigatePage() {
  const project = useActiveProject();
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<ExplanationMode>("manager");
  const [correlationKey, setCorrelationKey] = useState("");
  const [timeWindow, setTimeWindow] = useState("24h");

  const {
    messages,
    streaming,
    error,
    pipeline,
    sources,
    issueType,
    issueConfidence,
    issueReason,
    hasMessages,
    submit,
    reset,
  } = useChatStream();

  function onSubmit(e: { preventDefault: () => void }) {
    e.preventDefault();
    const q = input.trim();
    if (!q || streaming) {
      return;
    }
    void submit(q);
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
    error,
    pipeline,
    sources,
    issueType,
    issueConfidence,
    issueReason,
    reset,
    onSubmit,
    hasMessages,
  };
}
