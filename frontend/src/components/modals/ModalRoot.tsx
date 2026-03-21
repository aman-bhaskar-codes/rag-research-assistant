"use client";

import { useUIStore } from "@/stores/ui-store";
import SettingsModal from "./SettingsModal";

export default function ModalRoot() {
  const { activeModal, closeModal } = useUIStore();

  if (!activeModal) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center animate-in fade-in duration-200 p-4">
      <div 
        className="bg-[#0B0F17] w-full max-w-[700px] h-[80vh] rounded-2xl p-6 relative flex flex-col shadow-2xl border border-gray-800 animate-in zoom-in-95 duration-200"
      >
        <button
          onClick={closeModal}
          className="absolute top-4 right-4 text-gray-400 hover:text-white bg-gray-900 hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center transition-colors shadow-sm"
        >
          ✕
        </button>

        <div className="flex-1 overflow-hidden flex flex-col">
          {activeModal === "settings" && <SettingsModal />}
          {activeModal === "profile" && <div className="text-white p-4">Profile settings coming soon</div>}
          {activeModal === "memory" && <div className="text-white p-4">Memory visualizer coming soon</div>}
          {activeModal === "upgrade" && <div className="text-white p-4">Premium tier upgrade flow coming soon</div>}
        </div>
      </div>
    </div>
  );
}
