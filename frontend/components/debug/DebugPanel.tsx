"use client";

import { useUIStore } from "@/stores/ui-store";
import { useChatStore } from "@/features/chat/store";
import { useSettingsStore } from "@/features/settings/store";
import { X, Activity, Database, Cpu } from "lucide-react";

export default function DebugPanel() {
  const { debugMode, toggleDebug } = useUIStore();
  const { messages, isStreaming, selectedChatId } = useChatStore();
  const settings = useSettingsStore();

  if (!debugMode) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 w-80 bg-[#0F172A]/95 backdrop-blur-md border border-gray-700/50 rounded-xl shadow-2xl flex flex-col overflow-hidden text-xs font-mono origin-bottom-right animate-in fade-in slide-in-from-bottom-8 duration-200">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-700/50 bg-[#1E293B]/50">
        <div className="flex items-center gap-2 text-cyan-400 font-semibold tracking-wide uppercase">
          <Activity className="w-4 h-4" /> System Tracer
        </div>
        <button onClick={toggleDebug} className="text-gray-400 hover:text-white transition-colors">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4 max-h-[60vh] overflow-y-auto">
        {/* Settings State */}
        <div>
          <h3 className="text-gray-500 mb-2 flex items-center gap-1 uppercase tracking-widest text-[10px]">
            <Cpu className="w-3 h-3" /> State & Configuration
          </h3>
          <div className="bg-black/30 p-2.5 rounded text-gray-300 space-y-1 border border-black/20">
            <div className="flex justify-between">
              <span>Model:</span>
              <span className="text-blue-400">{settings.model}</span>
            </div>
            <div className="flex justify-between">
              <span>Temp:</span>
              <span className="text-gray-400">{settings.temperature}</span>
            </div>
            <div className="flex justify-between">
              <span>Chat ID:</span>
              <span className="text-pink-400 truncate max-w-[100px]">{selectedChatId || "null"}</span>
            </div>
            <div className="flex justify-between">
              <span>RAG:</span>
              <span className="text-green-400">{settings.rag.strategy} (k={settings.rag.top_k})</span>
            </div>
          </div>
        </div>

        {/* Live Streaming State */}
        <div>
           <h3 className="text-gray-500 mb-2 flex items-center gap-1 uppercase tracking-widest text-[10px]">
             <Database className="w-3 h-3" /> Pipeline Diagnostics
           </h3>
           <div className="bg-black/30 p-2.5 rounded text-gray-300 flex flex-col gap-1 border border-black/20">
              <div className="flex justify-between items-center">
                <span>Network Stream:</span> 
                <span className={isStreaming ? "text-yellow-400 animate-pulse flex items-center gap-1" : "text-gray-500"}>
                  {isStreaming ? (
                    <>
                      <div className="w-1.5 h-1.5 bg-yellow-400 rounded-full" /> ACTIVE
                    </>
                  ) : "IDLE"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Context Size:</span> 
                <span className="text-purple-400">{messages.length} objects</span>
              </div>
              {messages.length > 0 && messages[messages.length - 1].metadata && (
                <div className="flex justify-between">
                  <span>Last Latency:</span>
                  <span className="text-orange-400">{messages[messages.length - 1].metadata?.latency || 0}ms</span>
                </div>
              )}
           </div>
        </div>
      </div>
    </div>
  );
}
