import { useState } from "react";
import { motion } from "framer-motion";
import { Message } from "@/features/chat/types";
import { useModeStore } from "@/features/modes/store";
import SourceList from "../sources/SourceList";
import MarkdownRenderer from "../ui/MarkdownRenderer";
import MessageDebugPanel from "@/components/debug/MessageDebugPanel";

export default function MessageItem({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const [showSources, setShowSources] = useState(false);
  const currentMode = useModeStore((s) => s.mode);
  
  // Tie visual state immutably to the message node execution mode
  const mode = message.metadata?.mode || currentMode;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ease: "easeOut", duration: 0.3 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-xl w-full px-4 py-3 rounded-2xl text-sm leading-relaxed border ${
          isUser 
            ? "bg-blue-600 text-white border-transparent" 
            : mode === "ai_research"
            ? "bg-[#1E1B4B]/80 text-gray-200 shadow-md border-purple-900/40 backdrop-blur-sm"
            : mode === "programming"
            ? "bg-[#022C22]/80 text-gray-200 shadow-md border-green-900/40 backdrop-blur-sm"
            : "bg-[#1E293B]/80 text-gray-200 shadow-md border-gray-700/50 backdrop-blur-sm"
        }`}
      >
        {!isUser && mode === "programming" && (
          <div className="text-[10px] text-green-400 mb-2 uppercase tracking-widest font-semibold opacity-80 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500" /> Code Assistant Mode
          </div>
        )}

        {!isUser && mode === "ai_research" && (
          <div className="text-[10px] text-purple-400 mb-2 uppercase tracking-widest font-semibold opacity-80 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-500" /> Research Mode • Sources prioritized
          </div>
        )}

        {!isUser && mode === "business" && (
          <div className="text-[10px] text-yellow-500 mb-2 uppercase tracking-widest font-semibold opacity-80 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-yellow-500" /> Business Insights Mode
          </div>
        )}

        <div className="relative group/content">
          <MarkdownRenderer content={message.content} />
          
          {!isUser && !message.isStreaming && (
            <div className="absolute top-0 right-0 -mr-12 opacity-0 group-hover/content:opacity-100 transition-opacity flex flex-col gap-1">
              <button 
                onClick={() => navigator.clipboard.writeText(message.content)}
                className="p-1.5 rounded-lg bg-gray-800/80 hover:bg-gray-700 text-gray-400 hover:text-white transition-all shadow-lg"
                title="Copy"
              >
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
              </button>
              {message.content.includes("[ERROR]") && (
                 <button 
                  onClick={() => window.location.reload()} // Quick dirty retry for now
                  className="p-1.5 rounded-lg bg-red-900/80 hover:bg-red-800 text-red-200 hover:text-white transition-all shadow-lg"
                  title="Retry"
                >
                  <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M23 4v6h-6"></path><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
                </button>
              )}
            </div>
          )}
        </div>
        
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 border-t border-gray-700/50 pt-2">
            <button
              onClick={() => setShowSources(!showSources)}
              className={`text-[10px] uppercase font-bold tracking-widest transition-all flex items-center gap-1 ${
                showSources ? "text-purple-400" : "text-gray-500 hover:text-gray-300"
              }`}
            >
              {showSources ? "↑ Hide citations" : `↓ View ${message.sources.length} citations`}
            </button>

            {showSources && <SourceList sources={message.sources} />}
          </div>
        )}

        {message.metadata && <MessageDebugPanel data={message.metadata} />}
      </div>
    </motion.div>
  );
}
