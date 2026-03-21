"use client";

import { useChatStore } from "@/features/chat/store";
import MessageItem from "./MessageItem";
import { useAutoScroll } from "@/hooks/use-auto-scroll";

export default function MessageList() {
  const { messages, partialMessage, isStreaming } = useChatStore();
  
  // Use the auto-scroll hook we built earlier instead of simple useEffect
  const { containerRef, isAtBottom } = useAutoScroll<HTMLDivElement>([
    messages,
    partialMessage,
  ]);

  return (
    <div 
      className="space-y-4 animate-fadeIn h-full overflow-y-auto w-full pr-4"
      ref={containerRef}
    >
      <div className="max-w-4xl mx-auto space-y-4 pb-4">
        {messages.map((msg) => (
          <MessageItem key={msg.id} message={msg} />
        ))}

        {/* Streaming Message */}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="max-w-xl px-4 py-3 rounded-2xl text-sm bg-[#1E293B] text-gray-200">
              <span className="whitespace-pre-wrap">{partialMessage}</span>
              <span className="ml-1 animate-pulse">▍</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
