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
          <div className="flex flex-col justify-start gap-3">
            {!partialMessage ? (
              <div className="flex flex-col gap-3 max-w-xl">
                 <div className="flex items-center gap-2 px-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-ping" />
                    <span className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">Researching source documents...</span>
                 </div>
                 <div className="space-y-2 p-4 bg-white/5 border border-gray-800/40 rounded-2xl">
                    <div className="h-2 w-full bg-gray-800 rounded animate-pulse" />
                    <div className="h-2 w-5/6 bg-gray-800 rounded animate-pulse" />
                    <div className="h-2 w-2/3 bg-gray-800 rounded animate-pulse" />
                 </div>
              </div>
            ) : (
              <>
                <div className="text-[10px] text-gray-500 animate-pulse px-2 flex items-center gap-1.5 font-medium tracking-wide uppercase">
                  <span className="w-1 h-1 rounded-full bg-blue-400" /> Synthesizing final response...
                </div>
                <div className="flex justify-start">
                  <div className="max-w-xl px-4 py-3 rounded-2xl text-sm bg-[#1E1B4B]/80 backdrop-blur-md shadow-2xl border border-purple-900/30 text-gray-200">
                    <span className="whitespace-pre-wrap">{partialMessage}</span>
                    <span className="ml-1 animate-pulse text-blue-400">▍</span>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
