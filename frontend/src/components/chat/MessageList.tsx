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
          <div className="flex flex-col justify-start gap-2">
            <div className="text-xs text-gray-500 animate-pulse px-2 flex items-center gap-1.5 font-medium tracking-wide">
              Retrieving knowledge • Reranking • Generating...
            </div>
            <div className="flex justify-start">
              <div className="max-w-xl px-4 py-3 rounded-2xl text-sm bg-white/5 backdrop-blur-md shadow-2xl border border-gray-700/30 text-gray-200">
                <span className="whitespace-pre-wrap">{partialMessage}</span>
                <span className="ml-1 animate-pulse text-blue-400">▍</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
