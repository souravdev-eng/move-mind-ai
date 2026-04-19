import { useCallback, useEffect, useRef, useState } from "react";

import { type ChatMessage } from "@/interfaces/domain";
import { cannedTranscript } from "@/mocks";

interface State {
  messages: ChatMessage[];
  streaming: boolean;
}

export function useSimulatedStream(): {
  messages: ChatMessage[];
  streaming: boolean;
  submit: (question: string) => void;
  reset: () => void;
} {
  const [state, setState] = useState<State>({ messages: [], streaming: false });
  const timers = useRef<number[]>([]);

  const clearTimers = useCallback(() => {
    timers.current.forEach((t) => {
      window.clearTimeout(t);
    });
    timers.current = [];
  }, []);

  const reset = useCallback(() => {
    clearTimers();
    setState({ messages: [], streaming: false });
  }, [clearTimers]);

  const submit = useCallback(
    (question: string) => {
      clearTimers();
      const first: ChatMessage = {
        id: `u_${String(Date.now())}`,
        role: "user",
        content: question,
        createdAtIso: new Date().toISOString(),
      };
      setState({ messages: [first], streaming: true });

      cannedTranscript.slice(1).forEach((msg, i) => {
        const delay = (i + 1) * 900;
        const t = window.setTimeout(() => {
          setState((prev) => {
            const isLast = i === cannedTranscript.length - 2;
            return {
              messages: [...prev.messages, msg],
              streaming: !isLast,
            };
          });
        }, delay);
        timers.current.push(t);
      });
    },
    [clearTimers]
  );

  useEffect(
    () => () => {
      clearTimers();
    },
    [clearTimers]
  );

  return { messages: state.messages, streaming: state.streaming, submit, reset };
}
