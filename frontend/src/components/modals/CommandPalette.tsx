"use client";

import { useState } from "react";
import { useUIStore } from "@/stores/ui-store";

const commands = [
  { label: "⚙️ Open Settings", action: "settings" },
  { label: "🧠 View Memory", action: "memory" },
  { label: "✨ Upgrade Plan", action: "upgrade" },
  { label: "💬 New Chat", action: "new_chat" },
  { label: "🐛 Toggle Debug Mode", action: "debug" },
];

export default function CommandPalette() {
  const { openModal, closeModal, toggleDebug } = useUIStore();
  const [query, setQuery] = useState("");

  const filtered = commands.filter((c) =>
    c.label.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full rounded-2xl overflow-hidden shadow-2xl">
      <input
        autoFocus
        placeholder="Type a command or search..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full p-5 bg-[#080C13] outline-none text-base border-b border-gray-800 text-gray-200 placeholder-gray-500 font-medium"
      />

      <div className="p-2 space-y-1 bg-[#020617] max-h-[400px] overflow-y-auto">
        {filtered.map((cmd, i) => (
          <div
            key={i}
            onClick={async () => {
              closeModal();
              if (cmd.action === "new_chat") {
                const { clearMessages } = (await import("@/features/chat/store")).useChatStore.getState();
                clearMessages();
              } else if (cmd.action === "debug") {
                toggleDebug();
              } else {
                openModal(cmd.action as any);
              }
            }}
            className="px-4 py-3 rounded-xl hover:bg-[#1E293B] cursor-pointer text-sm text-gray-300 transition-colors"
          >
            {cmd.label}
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="p-4 text-center text-gray-500 text-sm">No commands found.</div>
        )}
      </div>
    </div>
  );
}
