import Sidebar from "@/components/sidebar/Sidebar";
import ChatContainer from "@/components/chat/ChatContainer";
import SettingsPanel from "@/components/settings/SettingsPanel";

export default function Home() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-[#0B0F17] text-white">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <ChatContainer />
      </div>

      {/* Right Panels */}
      <SettingsPanel />
    </div>
  );
}
