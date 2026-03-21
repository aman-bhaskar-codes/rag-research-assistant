import apiClient from "@/lib/api-client";
import type { Chat, ChatListItem } from "./types";

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


