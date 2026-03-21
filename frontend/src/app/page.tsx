"use client";

import Sidebar from "@/components/sidebar/Sidebar";
import ChatContainer from "@/components/chat/ChatContainer";
import ModalRoot from "@/components/modals/ModalRoot";
import UploadModal from "@/components/upload/UploadModal";
import DebugPanel from "@/components/debug/DebugPanel";
import { useUIStore } from "@/stores/ui-store";

export default function Home() {
  const uploadModalOpen = useUIStore((s) => s.uploadModalOpen);

  return (
    <div className="flex h-screen w-full overflow-hidden relative bg-[#020617]">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 shadow-[-10px_0_30px_-15px_rgba(0,0,0,0.5)] z-10">
        <ChatContainer />
      </div>

      {uploadModalOpen && <UploadModal />}
      <ModalRoot />
      <DebugPanel />
    </div>
  );
}
