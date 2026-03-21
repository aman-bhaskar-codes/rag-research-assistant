"use client";

import Sidebar from "@/components/sidebar/Sidebar";
import ChatContainer from "@/components/chat/ChatContainer";
import SettingsPanel from "@/components/settings/SettingsPanel";
import UploadModal from "@/components/upload/UploadModal";
import { useUIStore } from "@/stores/ui-store";

export default function Home() {
  const uploadModalOpen = useUIStore((s) => s.uploadModalOpen);

  return (
    <div className="flex h-screen w-full overflow-hidden relative">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <ChatContainer />
      </div>

      {/* Right Panels */}
      <SettingsPanel />

      {uploadModalOpen && <UploadModal />}
    </div>
  );
}
