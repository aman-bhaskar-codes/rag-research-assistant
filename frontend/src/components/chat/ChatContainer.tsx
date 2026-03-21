import ChatInput from "./ChatInput";
import MessageList from "./MessageList";

export default function ChatContainer() {
  return (
    <div className="flex flex-col h-full w-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <MessageList />
      </div>

      {/* Input */}
      <ChatInput />
    </div>
  );
}
