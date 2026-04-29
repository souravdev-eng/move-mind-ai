import { useEffect, useState } from "react";

import { getConversation, getConversationBySessionId } from "@/api/conversationClient";
import { useActiveProject } from "@/hooks/useActiveProject";
import { useChatStream } from "@/hooks/useChatStream";
import { type ChatMessage } from "@/interfaces/domain";

export function useInvestigatePage() {
  const project = useActiveProject();
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

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
    setSessionId,
    setMessages,
    sessionId,
  } = useChatStream();

  // Refresh sidebar when messages change
  useEffect(() => {
    if (hasMessages && !streaming) {
      setRefreshTrigger((prev) => prev + 1);
    }
  }, [hasMessages, streaming]);

  function onSubmit(e: { preventDefault: () => void }) {
    e.preventDefault();
    const q = input.trim();
    if (!q || streaming) {
      return;
    }
    void submit(q);
    setInput("");
  }

  async function handleSelectConversation(selectedSessionId: string) {
    setSessionId(selectedSessionId);

    try {
      // Fetch conversation with messages from backend
      const conversation = await getConversationBySessionId(selectedSessionId);
      const fullConversation = await getConversation(conversation.id, true);

      // Convert backend messages to frontend ChatMessage format
      const chatMessages: ChatMessage[] = fullConversation.messages.map((msg): ChatMessage => ({
        id: msg.id,
        role: msg.role === "human" ? "user" : "assistant",
        content: msg.content,
        createdAtIso: msg.created_at,
      }));

      setMessages(chatMessages);
    } catch (error) {
      console.error("Failed to load conversation history:", error);
    }
  }

  function handleNewConversation() {
    reset();
    setInput("");
    setSessionId(null);
  }

  return {
    project,
    input,
    setInput,
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
    sidebarOpen,
    setSidebarOpen,
    handleSelectConversation,
    handleNewConversation,
    sessionId,
    refreshTrigger,
  };
}
