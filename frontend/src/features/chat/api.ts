import apiClient from "@/lib/api-client";
import { streamChat } from "@/lib/stream";
import type { StreamCallbacks, StreamRequestBody } from "@/lib/stream";
import type { Chat, ChatListItem, SendMessageRequest } from "./types";

// ─── Chat API ────────────────────────────────────────────────────────────────

/**
 * Fetch all chats (sidebar list)
 */
export async function getChats(): Promise<ChatListItem[]> {
  const { data } = await apiClient.get<ChatListItem[]>("/chats");
  return data;
}

/**
 * Fetch a single chat with full messages
 */
export async function getChat(chatId: string): Promise<Chat> {
  const { data } = await apiClient.get<Chat>(`/chats/${chatId}`);
  return data;
}

/**
 * Create a new chat session
 */
export async function createChat(): Promise<Chat> {
  const { data } = await apiClient.post<Chat>("/chats");
  return data;
}

/**
 * Delete a chat session
 */
export async function deleteChat(chatId: string): Promise<void> {
  await apiClient.delete(`/chats/${chatId}`);
}

/**
 * Send a message via SSE streaming
 *
 * @returns AbortController to cancel the stream
 */
export function sendMessage(
  request: SendMessageRequest,
  callbacks: StreamCallbacks
): AbortController {
  const body: StreamRequestBody = {
    message: request.message,
    chat_id: request.chat_id,
    settings: request.settings,
  };

  return streamChat("/chat", body, callbacks);
}
