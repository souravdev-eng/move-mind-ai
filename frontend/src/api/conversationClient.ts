import {
  type BackendConversation,
  type BackendConversationWithMessages,
} from "@/interfaces/domain";

const BASE_URL = "/api/v1";

export async function listConversations(skip = 0, limit = 50): Promise<BackendConversation[]> {
  const res = await fetch(`${BASE_URL}/conversations?skip=${String(skip)}&limit=${String(limit)}`);
  if (!res.ok) {
    throw new Error(`Failed to list conversations: ${String(res.status)}`);
  }
  return res.json() as Promise<BackendConversation[]>;
}

export async function getConversation(
  id: string,
  includeMessages = true
): Promise<BackendConversationWithMessages> {
  const res = await fetch(
    `${BASE_URL}/conversations/${id}?include_messages=${String(includeMessages)}`
  );
  if (!res.ok) {
    throw new Error(`Failed to get conversation: ${String(res.status)}`);
  }
  return res.json() as Promise<BackendConversationWithMessages>;
}

export async function getConversationBySessionId(sessionId: string): Promise<BackendConversation> {
  const res = await fetch(`${BASE_URL}/conversations/by-session/${sessionId}`);
  if (!res.ok) {
    throw new Error(`Failed to get conversation by session: ${String(res.status)}`);
  }
  return res.json() as Promise<BackendConversation>;
}
