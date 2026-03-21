"use client";

import { useUIStore } from "@/stores/ui-store";

export default function DebugSettings() {
  const { debugMode, toggleDebug } = useUIStore();

  return (
    <div className="space-y-4 pt-4 border-t border-gray-800">
      <div className="flex items-center justify-between text-sm">
        <div className="space-y-0.5">
          <h3 className="font-medium text-gray-300">Debug Mode</h3>
          <p className="text-[10px] text-gray-500">Show Retrieval Trace Data</p>
        </div>
        <input 
          type="checkbox" 
          checked={debugMode} 
          onChange={toggleDebug} 
          className="rounded bg-[#1E293B] border-gray-700 text-blue-600 focus:ring-blue-500" 
        />
      </div>
    </div>
  );
}
