"use client";

import { useUIStore } from "@/stores/ui-store";
import { useChats, useCreateChat } from "@/features/chat/hooks";
import { useChatStore } from "@/features/chat/store";

export default function Sidebar() {
  const toggleSettingsPanel = useUIStore((s) => s.toggleSettingsPanel);
  const { data: chats, isLoading } = useChats();
  const { mutate: createChat, isPending } = useCreateChat();
  
  const selectedChatId = useChatStore((s) => s.selectedChatId);
  const setSelectedChat = useChatStore((s) => s.setSelectedChat);

  return (
    <div className="w-64 bg-[#0F172A] border-r border-gray-800 flex flex-col h-full flex-shrink-0">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 font-semibold flex-shrink-0">
        RAG Assistant
      </div>

      {/* New Chat & Upload */}
      <div className="p-4 flex flex-col gap-2 flex-shrink-0 border-b border-gray-800/50">
        <button 
          onClick={() => createChat()}
          disabled={isPending}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg py-2 text-sm transition-colors cursor-pointer font-medium"
        >
          {isPending ? "Creating..." : "+ New Chat"}
        </button>
        <button 
          onClick={() => useUIStore.getState().toggleUploadModal()}
          className="w-full bg-gray-800 hover:bg-gray-700 rounded-lg py-2 text-sm transition-colors cursor-pointer text-gray-300"
        >
          Upload Document
        </button>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
        {isLoading ? (
          <div className="px-2 text-sm text-gray-500 animate-pulse">Loading history...</div>
        ) : !chats?.length ? (
          <div className="px-2 text-sm text-gray-500">No conversations yet</div>
        ) : (
          chats.map((chat) => (
            <button
              key={chat.id}
              onClick={() => setSelectedChat(chat.id)}
              className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors truncate ${
                selectedChatId === chat.id 
                  ? "bg-[#1E293B] text-white font-medium" 
                  : "text-gray-400 hover:bg-[#1E293B] hover:text-gray-200"
              }`}
            >
              {chat.title || "New Conversation"}
            </button>
          ))
        )}
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
