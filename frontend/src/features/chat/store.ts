import { create } from "zustand";
import type { Message, Source } from "./types";
import { generateId } from "@/lib/utils";

// ─── Chat Store ──────────────────────────────────────────────────────────────

interface ChatState {
  /** Current chat messages */
  messages: Message[];
  /** Whether a response is currently streaming */
  isStreaming: boolean;
  /** Accumulated partial message during streaming */
  partialMessage: string;
  /** Currently selected chat ID */
  selectedChatId: string | null;
  /** Sources for the latest assistant message */
  currentSources: Source[];
  /** AbortController for cancelling active stream */
  streamController: AbortController | null;

  // ── Actions ──────────────────────────────────────────────────────────────

  /** Add a complete message to the list */
  addMessage: (message: Omit<Message, "id" | "createdAt">) => void;
  /** Start streaming: add a placeholder assistant message */
  startStream: (controller: AbortController) => void;
  /** Append a token to the streaming message */
  appendToken: (token: string) => void;
  /** Finalize the stream: mark assistant message as complete */
  finalizeStream: (sources?: Source[]) => void;
  /** Cancel the active stream */
  cancelStream: () => void;
  /** Set the selected chat and load its messages */
  setSelectedChat: (chatId: string | null, messages?: Message[]) => void;
  /** Set sources for the current response */
  setSources: (sources: Source[]) => void;
  /** Clear all messages (for new chat) */
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isStreaming: false,
  partialMessage: "",
  selectedChatId: null,
  currentSources: [],
  streamController: null,

  addMessage: (msg) =>
    set((s) => ({
      messages: [
        ...s.messages,
        {
          ...msg,
          id: generateId(),
          createdAt: new Date().toISOString(),
        },
      ],
    })),

  startStream: (controller) =>
    set((s) => ({
      isStreaming: true,
      partialMessage: "",
      currentSources: [],
      streamController: controller,
      messages: [
        ...s.messages,
        {
          id: generateId(),
          role: "assistant" as const,
          content: "",
          createdAt: new Date().toISOString(),
          isStreaming: true,
        },
      ],
    })),

  appendToken: (token) =>
    set((s) => {
      const newPartial = s.partialMessage + token;
      const messages = [...s.messages];
      const lastMsg = messages[messages.length - 1];
      if (lastMsg && lastMsg.isStreaming) {
        messages[messages.length - 1] = {
          ...lastMsg,
          content: newPartial,
        };
      }
      return { partialMessage: newPartial, messages };
    }),

  finalizeStream: (sources) =>
    set((s) => {
      const messages = [...s.messages];
      const lastMsg = messages[messages.length - 1];
      if (lastMsg && lastMsg.isStreaming) {
        messages[messages.length - 1] = {
          ...lastMsg,
          isStreaming: false,
          sources: sources || s.currentSources,
        };
      }
      return {
        messages,
        isStreaming: false,
        partialMessage: "",
        streamController: null,
        currentSources: sources || s.currentSources,
      };
    }),

  cancelStream: () => {
    const { streamController } = get();
    if (streamController) {
      streamController.abort();
    }
    set((s) => {
      const messages = [...s.messages];
      const lastMsg = messages[messages.length - 1];
      if (lastMsg && lastMsg.isStreaming) {
        messages[messages.length - 1] = {
          ...lastMsg,
          isStreaming: false,
          content: lastMsg.content || "(cancelled)",
        };
      }
      return {
        messages,
        isStreaming: false,
        partialMessage: "",
        streamController: null,
      };
    });
  },

  setSelectedChat: (chatId, messages) =>
    set({
      selectedChatId: chatId,
      messages: messages || [],
      isStreaming: false,
      partialMessage: "",
      currentSources: [],
    }),

  setSources: (sources) => set({ currentSources: sources }),

  clearMessages: () =>
    set({
      messages: [],
      selectedChatId: null,
      isStreaming: false,
      partialMessage: "",
      currentSources: [],
    }),
}));
