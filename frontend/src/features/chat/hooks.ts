import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getChats, getChat, createChat, deleteChat } from "./api";

// ─── Query Keys ──────────────────────────────────────────────────────────────

export const chatKeys = {
  all: ["chats"] as const,
  list: () => [...chatKeys.all, "list"] as const,
  detail: (id: string) => [...chatKeys.all, "detail", id] as const,
};

// ─── Hooks ───────────────────────────────────────────────────────────────────

/**
 * Fetch all chats for the sidebar
 */
export function useChats() {
  return useQuery({
    queryKey: chatKeys.list(),
    queryFn: getChats,
    staleTime: 30_000, // 30 seconds
  });
}

/**
 * Fetch a single chat with messages
 */
export function useChat(chatId: string | null) {
  return useQuery({
    queryKey: chatKeys.detail(chatId!),
    queryFn: () => getChat(chatId!),
    enabled: !!chatId,
  });
}

/**
 * Create a new chat
 */
export function useCreateChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createChat,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: chatKeys.list() });
    },
  });
}

/**
 * Delete a chat
 */
export function useDeleteChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteChat,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: chatKeys.list() });
    },
  });
}


