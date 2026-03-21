import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getChats, getChat, createChat, deleteChat, sendMessage } from "./api";
import { useChatStore } from "./store";
import { useSettingsStore } from "@/features/settings/store";
import type { SendMessageRequest } from "./types";

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

/**
 * Send a message with streaming support
 *
 * This orchestrates the full message lifecycle:
 * 1. Optimistic UI update (add user message)
 * 2. Start streaming (add placeholder assistant message)
 * 3. Append tokens as they arrive
 * 4. Finalize with sources
 */
export function useSendMessage() {
  const {
    addMessage,
    startStream,
    appendToken,
    finalizeStream,
    cancelStream,
  } = useChatStore();
  const settings = useSettingsStore();
  const queryClient = useQueryClient();

  const send = (message: string, chatId?: string) => {
    // 1. Optimistic: add user message immediately
    addMessage({ role: "user", content: message });

    const request: SendMessageRequest = {
      message,
      chat_id: chatId,
      settings: {
        model: settings.model,
        temperature: settings.temperature,
        rag: { ...settings.rag },
        memory: { ...settings.memory },
      },
    };

    // 2. Start streaming
    const controller = sendMessage(request, {
      onToken: (token) => {
        appendToken(token);
      },
      onSources: (sources) => {
        useChatStore.getState().setSources(sources);
      },
      onDone: () => {
        finalizeStream();
        // Refresh chat list (title may have been generated)
        queryClient.invalidateQueries({ queryKey: chatKeys.list() });
      },
      onError: (error) => {
        console.error("Stream error:", error);
        finalizeStream();
      },
    });

    startStream(controller);
  };

  return { send, cancel: cancelStream };
}
