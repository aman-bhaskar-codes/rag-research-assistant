"use client";

import { useUIStore } from "@/stores/ui-store";
import { Settings } from "lucide-react";
import ProfileDropdown from "../profile/ProfileDropdown";

export default function TopBar() {
  const { openModal } = useUIStore();

  return (
    <div className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-[#0B0F17] flex-shrink-0 z-10 w-full shadow-sm">
      <div className="text-sm text-gray-400 flex items-center gap-2">
        <span className="font-semibold text-gray-200">RAG</span> 
        <span className="text-gray-500">|</span> 
        <span>Research Assistant</span>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={() => openModal("settings")}
          className="text-gray-400 hover:text-white transition-colors p-1.5 rounded-md hover:bg-gray-800 flex items-center gap-2 text-sm"
          title="Settings"
        >
          <Settings size={16} /> <span className="hidden sm:inline">Settings</span>
        </button>

        <ProfileDropdown />
      </div>
    </div>
  );
}
