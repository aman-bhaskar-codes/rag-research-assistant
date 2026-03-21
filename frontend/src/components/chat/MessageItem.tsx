"use client";

import { Message } from "@/features/chat/types";
import SourceCard from "../sources/SourceCard";

export default function MessageItem({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-xl px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser ? "bg-blue-600 text-white" : "bg-[#1E293B] text-gray-200"
        }`}
      >
        {message.content}
        
        {message.sources && message.sources.length > 0 && (
          <div className="mt-4 flex flex-col gap-2">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Sources</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {message.sources.map((src, i) => (
                <SourceCard key={i} source={src} index={i} />
              ))}
            </div>
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
