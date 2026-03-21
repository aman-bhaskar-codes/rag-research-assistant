"use client";

import { useSettingsStore } from "@/features/settings/store";

export default function MemorySettings() {
  const settings = useSettingsStore();

  return (
    <div className="space-y-4 pt-4 border-t border-gray-800">
      <div className="flex items-center justify-between">
        <div className="space-y-0.5">
          <h3 className="text-sm font-medium text-gray-300">Conversation Memory</h3>
          <p className="text-[10px] text-gray-500">Provide past context to LLM</p>
        </div>
        <input
          type="checkbox"
          checked={settings.memory.enabled}
          onChange={(e) => settings.updateMemory({ enabled: e.target.checked })}
          className="rounded bg-[#1E293B] border-gray-700 text-blue-600 focus:ring-blue-500"
        />
      </div>
    </div>
  );
}
