"use client";

import { useState } from "react";
import { useChatStore } from "@/features/chat/store";
import { useModeStore } from "@/features/modes/store";
import { useSettingsStore } from "@/features/settings/store";
import { streamChat } from "@/lib/stream";
import { v4 as uuidv4 } from "uuid";

export default function ChatInput() {
  const [input, setInput] = useState("");
  
  const { mode } = useModeStore();
  const settings = useSettingsStore();

  const addMessage = useChatStore((s) => s.addMessage);
  const startStreaming = useChatStore((s) => s.startStream);
  const updatePartial = useChatStore((s) => s.updatePartial);
  const finishStreaming = useChatStore((s) => s.finalizeStreamWithCompleteMessage);
  const setError = useChatStore((s) => s.setError);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: uuidv4(),
      role: "user" as const,
      content: input,
      createdAt: new Date().toISOString(),
    };

    addMessage(userMessage);
    
    // We pass a dummy controller since the user's code relies on manual startStreaming
    startStreaming(new AbortController());

    let accumulated = "";

    await streamChat({
      query: input,
      metadata: {
        mode,
        model: settings.model,
        rag: {
          strategy: settings.rag.strategy,
          top_k: settings.rag.top_k,
        },
      },

      onToken: (token) => {
        accumulated += token;
        updatePartial(accumulated);
      },

      onDone: (data) => {
        finishStreaming({
          id: uuidv4(),
          role: "assistant",
          content: accumulated,
          sources: data?.sources || [],
          metadata: { mode, latency: data?.latency, strategy: settings.rag.strategy, chunks: data?.chunks || [] },
          createdAt: new Date().toISOString(),
        });
      },

      onError: (err) => {
        console.error(err);
        setError(err instanceof Error ? err.message : String(err));
      },
    });

    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-800 p-4 shrink-0 transition-all bg-[#0B0F17]">
      <div className="flex items-center gap-2 max-w-4xl mx-auto">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything..."
          className="flex-1 bg-[#1E293B] rounded-lg px-4 py-3 text-sm outline-none border border-transparent focus:border-gray-700 transition-colors"
        />

        <button
          onClick={handleSend}
          className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg text-sm font-medium transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={!input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
