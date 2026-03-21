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
  addMessage: (message: Partial<Message> & { role: "user" | "assistant", content: string }) => void;
  /** Start streaming: add a placeholder assistant message */
  startStream: (controller: AbortController) => void;
  /** Replace the partial message entirely */
  updatePartial: (text: string) => void;
  /** Finalize the stream by pushing a complete message and clearing partial */
  finalizeStreamWithCompleteMessage: (finalMessage: Message) => void;
  
  /** Cancel the active stream */
  cancelStream: () => void;
  /** Set the selected chat and load its messages */
  setSelectedChat: (chatId: string | null, messages?: Message[]) => void;
  /** Set sources for the current response */
  setSources: (sources: Source[]) => void;
  /** Clear all messages (for new chat) */
  clearMessages: () => void;

  /** Error state */
  error: string | null;
  setError: (err: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isStreaming: false,
  partialMessage: "",
  selectedChatId: null,
  currentSources: [],
  streamController: null,
  error: null,

  setError: (err) => set({ error: err }),

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

  updatePartial: (text) =>
    set(() => ({
      partialMessage: text,
    })),

  finalizeStreamWithCompleteMessage: (finalMessage) =>
    set((s) => ({
      messages: [...s.messages.filter(m => !m.isStreaming), finalMessage],
      isStreaming: false,
      partialMessage: "",
      streamController: null,
    })),

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
