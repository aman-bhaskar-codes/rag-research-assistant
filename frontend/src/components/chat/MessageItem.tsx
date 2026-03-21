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

        <MarkdownRenderer content={message.content} />
        
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2 border-t border-gray-700/50 pt-2">
            <button
              onClick={() => setShowSources(!showSources)}
              className="text-xs text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
            >
              {showSources ? "Hide sources" : "View sources"}
            </button>

            {showSources && <SourceList sources={message.sources} />}
          </div>
        )}

        {message.metadata && <MessageDebugPanel data={message.metadata} />}
      </div>
    </motion.div>
  );
}
