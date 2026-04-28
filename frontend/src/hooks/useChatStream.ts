import { useCallback, useRef, useState } from "react";

import { streamChat } from "@/api/chatClient";
import {
  type AgentNodeName,
  type ChatMessage,
  type NodeStatus,
  type SourceDocumentDTO,
  type SSEEvent,
  type Verdict,
} from "@/interfaces/domain";

// ── Public state shape ────────────────────────────────────────────────────

export interface PipelineNode {
  name: AgentNodeName;
  status: NodeStatus;
}

export interface ChatStreamState {
  messages: ChatMessage[];
  streaming: boolean;
  error: string | null;
  sessionId: string | null;
  pipeline: PipelineNode[];
  sources: SourceDocumentDTO[];
  issueType: Verdict | null;
  issueConfidence: number | null;
  issueReason: string | null;
}

const INITIAL_STATE: ChatStreamState = {
  messages: [],
  streaming: false,
  error: null,
  sessionId: null,
  pipeline: [],
  sources: [],
  issueType: null,
  issueConfidence: null,
  issueReason: null,
};

// ── Hook ──────────────────────────────────────────────────────────────────

export function useChatStream() {
  const [state, setState] = useState<ChatStreamState>(INITIAL_STATE);
  const abortRef = useRef<AbortController | null>(null);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setState((prev) => ({ ...prev, streaming: false }));
  }, []);

  const reset = useCallback(() => {
    cancel();
    setState(INITIAL_STATE);
  }, [cancel]);

  const submit = useCallback(
    async (question: string) => {
      cancel();

      const userMsg: ChatMessage = {
        id: `u_${String(Date.now())}`,
        role: "user",
        content: question,
        createdAtIso: new Date().toISOString(),
      };

      const assistantId = `a_${String(Date.now())}`;

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMsg],
        streaming: true,
        error: null,
        pipeline: [],
        sources: [],
        issueType: null,
        issueConfidence: null,
        issueReason: null,
      }));

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const stream = streamChat(
          {
            message: question,
            stream: true,
            ...(state.sessionId != null ? { session_id: state.sessionId } : {}),
          },
          controller.signal
        );

        let tokenBuffer = "";

        for await (const event of stream) {
          handleEvent(event, assistantId, tokenBuffer, (updatedBuffer) => {
            tokenBuffer = updatedBuffer;
          });
        }
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        const message = err instanceof Error ? err.message : "Unknown error";
        setState((prev) => ({ ...prev, error: message, streaming: false }));
        return;
      }

      setState((prev) => ({ ...prev, streaming: false }));
    },
    [cancel, state.sessionId]
  );

  function handleEvent(
    event: SSEEvent,
    assistantId: string,
    tokenBuffer: string,
    setTokenBuffer: (v: string) => void
  ) {
    switch (event.type) {
      case "session":
        setState((prev) => ({ ...prev, sessionId: event.session_id }));
        break;

      case "status":
        setState((prev) => {
          const existing = prev.pipeline.find((n) => n.name === event.node);
          if (existing) return prev;
          return {
            ...prev,
            pipeline: [...prev.pipeline, { name: event.node, status: "running" as NodeStatus }],
          };
        });
        break;

      case "retrieval":
      case "rerank":
        // Mark previous pipeline node as done
        setState((prev) => {
          const pipeline = prev.pipeline.map((n) =>
            n.status === "running" ? { ...n, status: "done" as NodeStatus } : n
          );
          return { ...prev, pipeline };
        });
        break;

      case "token": {
        const newBuffer = tokenBuffer + event.content;
        setTokenBuffer(newBuffer);

        setState((prev) => {
          const last = prev.messages[prev.messages.length - 1];
          if (last?.id === assistantId) {
            // Update existing assistant message
            const updated: ChatMessage[] = [
              ...prev.messages.slice(0, -1),
              { ...last, content: newBuffer },
            ];
            return { ...prev, messages: updated };
          }
          // Create new assistant message
          const assistantMsg: ChatMessage = {
            id: assistantId,
            role: "assistant",
            content: newBuffer,
            createdAtIso: new Date().toISOString(),
          };
          return { ...prev, messages: [...prev.messages, assistantMsg] };
        });
        break;
      }

      case "sources":
        setState((prev) => {
          // Mark all pipeline nodes as done
          const pipeline = prev.pipeline.map((n) => ({
            ...n,
            status: "done" as NodeStatus,
          }));

          // Attach verdict to the assistant message
          const messages = prev.messages.map((m) =>
            m.id === assistantId && event.issue_type ? { ...m, verdict: event.issue_type } : m
          );

          return {
            ...prev,
            messages,
            pipeline,
            sources: event.sources,
            issueType: event.issue_type,
            issueConfidence: event.issue_confidence,
            issueReason: event.issue_classification_reason,
          };
        });
        break;

      case "done":
        setState((prev) => ({ ...prev, streaming: false }));
        break;
    }
  }

  return {
    ...state,
    submit,
    reset,
    cancel,
    hasMessages: state.messages.length > 0,
  };
}
