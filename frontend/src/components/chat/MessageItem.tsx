import { useState } from "react";
import { motion } from "framer-motion";
import { Message } from "@/features/chat/types";
import SourceList from "../sources/SourceList";
import MarkdownRenderer from "../ui/MarkdownRenderer";
import MessageDebugPanel from "../debug/MessageDebugPanel";

export default function MessageItem({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const [showSources, setShowSources] = useState(false);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ease: "easeOut", duration: 0.3 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-xl w-full px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser ? "bg-blue-600 text-white" : "bg-[#1E293B] text-gray-200 shadow-md"
        }`}
      >
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
