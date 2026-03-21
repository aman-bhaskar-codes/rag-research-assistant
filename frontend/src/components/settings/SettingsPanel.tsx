"use client";

import { useUIStore } from "@/stores/ui-store";
import { useSettingsStore } from "@/features/settings/store";
import ModelSettings from "./sections/ModelSettings";
import RagSettings from "./sections/RagSettings";
import MemorySettings from "./sections/MemorySettings";
import DebugSettings from "./sections/DebugSettings";
import AccountSection from "./sections/AccountSection";

export default function SettingsPanel() {
  const { settingsPanelOpen, toggleSettingsPanel } = useUIStore();
  const resetSettings = useSettingsStore((s) => s.resetSettings);

  if (!settingsPanelOpen) return null;

  return (
    <div className="w-[320px] bg-[#0B0F17] border-l border-gray-800 flex flex-col h-full flex-shrink-0 animate-in slide-in-from-right-8 duration-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 flex justify-between items-center flex-shrink-0">
        <h2 className="font-semibold text-gray-200 tracking-wide uppercase text-sm">Settings Matrix</h2>
        <button
          onClick={toggleSettingsPanel}
          className="text-gray-400 hover:text-white transition-colors"
        >
          ✕
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        <ModelSettings />
        <RagSettings />
        <MemorySettings />
        <DebugSettings />
        <AccountSection />
      </div>
      
      {/* Footer / Reset Box */}
      <div className="p-4 border-t border-gray-800 flex-shrink-0 bg-[#0F172A]/50 backdrop-blur-sm">
         <button 
           onClick={resetSettings}
           className="w-full py-2 text-xs text-gray-500 hover:text-gray-300 border border-gray-800 hover:border-gray-600 rounded-lg transition-colors"
         >
           Reset Config to Defaults
         </button>
      </div>
    </div>
  );
}
