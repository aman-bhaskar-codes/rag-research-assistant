"use client";

import { useState } from "react";
import { useSendMessage } from "@/features/chat/hooks";

export default function ChatInput() {
  const [input, setInput] = useState("");
  const { send } = useSendMessage();

  const handleSend = () => {
    if (!input.trim()) return;

    send(input.trim());
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
