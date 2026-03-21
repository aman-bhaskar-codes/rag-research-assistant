"use client";

import { useSettingsStore } from "@/features/settings/store";
import { useUIStore } from "@/stores/ui-store";
import { MODEL_OPTIONS, RAG_STRATEGIES } from "@/config/constants";

export default function SettingsPanel() {
  const { settingsPanelOpen, toggleSettingsPanel } = useUIStore();
  const settings = useSettingsStore();

  if (!settingsPanelOpen) return null;

  return (
    <div className="w-80 bg-[#0B0F17] border-l border-gray-800 flex flex-col h-full flex-shrink-0">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 flex justify-between items-center flex-shrink-0">
        <h2 className="font-semibold text-gray-200">Settings</h2>
        <button
          onClick={toggleSettingsPanel}
          className="text-gray-400 hover:text-white transition-colors"
        >
          ✕
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Model Selection */}
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

        {/* Temperature */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex justify-between">
            <span>Temperature</span>
            <span className="text-blue-400">{settings.temperature}</span>
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={settings.temperature}
            onChange={(e) =>
              settings.updateSettings({ temperature: parseFloat(e.target.value) })
            }
            className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
        </div>

        {/* RAG Configuration */}
        <div className="space-y-4 pt-4 border-t border-gray-800">
          <h3 className="text-sm font-medium text-gray-300">RAG Settings</h3>

          <div className="space-y-2">
            <label className="text-xs text-gray-400">Retrieval Strategy</label>
            <select
              value={settings.rag.strategy}
              onChange={(e) =>
                settings.updateRAG({ strategy: e.target.value as any })
              }
              className="w-full bg-[#1E293B] border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 outline-none focus:border-blue-500 transition-colors"
            >
              {RAG_STRATEGIES.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center justify-between">
            <label className="text-xs text-gray-400">Rerank Results</label>
            <input
              type="checkbox"
              checked={settings.rag.rerank}
              onChange={(e) => settings.updateRAG({ rerank: e.target.checked })}
              className="rounded bg-[#1E293B] border-gray-700 text-blue-600 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <label className="text-xs text-gray-400">Top K Results</label>
            <input
              type="number"
              min="1"
              max="20"
              value={settings.rag.top_k}
              onChange={(e) => settings.updateRAG({ top_k: parseInt(e.target.value) || 5 })}
              className="w-16 bg-[#1E293B] border border-gray-700 rounded-md px-2 py-1 text-sm text-center text-gray-200 outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Memory Configuration */}
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
      </div>
      
      {/* Footer / Upgrades */}
      <div className="p-4 border-t border-gray-800 flex-shrink-0 space-y-4">
        {settings.plan !== "premium" && (
          <div className="p-3 bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-lg text-sm transition-all hover:border-purple-500/50 cursor-pointer">
            <p className="text-gray-200 font-medium text-xs">Unlock Gemini Pro & advanced RAG precision.</p>
            <button className="block mt-2 text-xs text-blue-400 font-medium hover:underline flex items-center gap-1">
              ✨ Upgrade to Premium
            </button>
          </div>
        )}
        <button 
          onClick={settings.resetSettings}
          className="w-full py-2 text-xs text-gray-500 hover:text-gray-300 border border-gray-800 hover:border-gray-600 rounded-lg transition-colors"
        >
          Reset Config to Defaults
        </button>
      </div>
    </div>
  );
}
