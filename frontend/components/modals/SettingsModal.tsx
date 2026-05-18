"use client";

import { useSettingsStore } from "@/features/settings/store";
import ModelSettings from "../settings/sections/ModelSettings";
import RagSettings from "../settings/sections/RagSettings";
import MemorySettings from "../settings/sections/MemorySettings";
import DebugSettings from "../settings/sections/DebugSettings";
import AccountSection from "../settings/sections/AccountSection";

export default function SettingsModal() {
  const resetSettings = useSettingsStore((s) => s.resetSettings);

  return (
    <div className="flex flex-col h-full text-left">
      <div className="mb-6 border-b border-gray-800 pb-4">
        <h2 className="text-xl font-semibold text-gray-200 tracking-wide">Settings Matrix</h2>
        <p className="text-sm text-gray-500 mt-1">Configure your AI models, retrieval protocols, and memory subsystems.</p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-6 pr-2">
        <ModelSettings />
        <RagSettings />
        <MemorySettings />
        <DebugSettings />
        <AccountSection />
      </div>

      <div className="mt-6 pt-4 border-t border-gray-800 flex-shrink-0">
         <button 
           onClick={resetSettings}
           className="w-full py-2.5 text-xs text-gray-500 hover:text-gray-300 border border-gray-800 hover:border-gray-600 rounded-lg transition-colors flex items-center justify-center gap-2"
         >
           ↺ Reset Config to Defaults
         </button>
      </div>
    </div>
  );
}
