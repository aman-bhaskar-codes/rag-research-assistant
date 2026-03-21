"use client";

import { useState } from "react";
import { Message } from "@/features/chat/types";
import SourceList from "../sources/SourceList";

export default function MessageItem({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const [showSources, setShowSources] = useState(false);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-xl px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser ? "bg-blue-600 text-white" : "bg-[#1E293B] text-gray-200"
        }`}
      >
        {message.content}
        
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

        {message.metadata && (
          <div className="mt-2 flex gap-2 text-[10px] text-gray-400 opacity-70">
            {message.metadata.model && <span>{message.metadata.model}</span>}
            {message.metadata.latency && <span>{message.metadata.latency}ms</span>}
          </div>
        )}
      </div>
    </div>
  );
}
