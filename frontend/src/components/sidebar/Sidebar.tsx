"use client";

import { useUIStore } from "@/stores/ui-store";

export default function Sidebar() {
  const toggleSettingsPanel = useUIStore((s) => s.toggleSettingsPanel);

  return (
    <div className="w-64 bg-[#0F172A] border-r border-gray-800 flex flex-col h-full flex-shrink-0">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 font-semibold flex-shrink-0">
        RAG Assistant
      </div>

      {/* New Chat */}
      <div className="p-4 flex-shrink-0">
        <button className="w-full bg-blue-600 hover:bg-blue-700 rounded-lg py-2 text-sm transition-colors cursor-pointer">
          + New Chat
        </button>
      </div>

      {/* Chat List Placeholder */}
      <div className="flex-1 overflow-y-auto px-4 py-2 text-sm text-gray-400">
        No conversations yet
      </div>
      
      {/* Footer */}
      <div className="p-4 border-t border-gray-800 flex-shrink-0 text-sm">
        <button 
          onClick={toggleSettingsPanel}
          className="w-full text-left text-gray-400 hover:text-white transition-colors flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-[#1E293B]"
        >
          ⚙️ Settings
        </button>
      </div>
    </div>
  );
}
