import { type SSEEvent } from "@/interfaces/domain";

export interface ChatRequestBody {
  message: string;
  session_id?: string;
  stream: boolean;
}

/**
 * POST /api/v1/chat with stream:true.
 * Returns an async iterator that yields typed SSEEvent objects.
 * Uses fetch + ReadableStream (NOT EventSource) for POST support.
 */
export async function* streamChat(
  body: ChatRequestBody,
  signal?: AbortSignal
): AsyncGenerator<SSEEvent> {
  const res = await fetch("/api/v1/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, stream: true }),
    signal: signal ?? null,
  });

  if (!res.ok) {
    throw new Error(`Chat API error: ${String(res.status)} ${res.statusText}`);
  }

  const reader = res.body?.getReader();
  if (!reader) {
    throw new Error("Response body is not readable");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      // Keep the last (possibly incomplete) line in the buffer
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.length === 0 || !trimmed.startsWith("data: ")) continue;

        const payload = trimmed.slice(6); // strip "data: "

        if (payload === "[DONE]") {
          yield { type: "done" } as SSEEvent;
          return;
        }

        try {
          yield JSON.parse(payload) as SSEEvent;
        } catch {
          // skip malformed lines
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
