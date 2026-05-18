"use client";

import { useSettingsStore } from "@/features/settings/store";
import { MODEL_OPTIONS } from "@/config/constants";

export default function ModelSettings() {
  const settings = useSettingsStore();

  return (
    <div className="space-y-2">
      <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
        Model Selection
      </label>
      <div className="space-y-1.5">
        {MODEL_OPTIONS.map((m) => {
          const isLocked = m.tier === "premium" && settings.plan !== "premium";

          return (
            <button
              key={m.value}
              onClick={() => !isLocked && settings.updateSettings({ model: m.value })}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors border ${
                settings.model === m.value
                  ? "bg-blue-600 border-blue-500 text-white"
                  : "bg-[#1E293B] border-transparent text-gray-300 hover:bg-[#273549]"
              } ${isLocked ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              <div className="flex items-center justify-between">
                <span>{m.label}</span>
                {isLocked && (
                  <span className="text-[10px] text-yellow-400 font-medium tracking-wide uppercase">
                    🔒 Premium
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
