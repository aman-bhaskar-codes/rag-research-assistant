import ChatInput from "./ChatInput";
import MessageList from "./MessageList";
import TopBar from "@/components/layout/TopBar";
import { useModeStore } from "@/features/modes/store";
import { MODE_CONFIG } from "@/features/modes/config";

export default function ChatContainer() {
  const { mode } = useModeStore();
  const config = MODE_CONFIG[mode];

  return (
    <div className="flex flex-col h-full w-full relative">
      <TopBar />
      
      {/* Mode Hint Overlay */}
      <div className="absolute top-[70px] left-0 right-0 flex justify-center z-10 pointer-events-none fade-in animate-in duration-500">
        <div className="bg-[#0B0F17]/80 backdrop-blur-md px-4 py-1.5 rounded-full border border-gray-800/80 text-[10px] text-gray-400 uppercase tracking-widest font-semibold shadow-sm flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full bg-gradient-to-r ${config.color}`} />
          <span className={config.textDecoration}>{config.label}:</span> 
          <span className="opacity-80 normal-case tracking-normal text-gray-300">{config.hint}</span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <MessageList />
      </div>

      {/* Input */}
      <ChatInput />
    </div>
  );
}
