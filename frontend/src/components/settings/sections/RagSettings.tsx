"use client";

import { useSettingsStore } from "@/features/settings/store";
import { RAG_STRATEGIES } from "@/config/constants";

export default function RagSettings() {
  const settings = useSettingsStore();

  return (
    <div className="space-y-4 pt-4 border-t border-gray-800">
      <h3 className="text-sm font-medium text-gray-300">RAG Settings</h3>

      <div className="space-y-2">
        <label className="text-xs text-gray-400">Retrieval Strategy</label>
        <select
          value={settings.rag.strategy}
          onChange={(e) => settings.updateRAG({ strategy: e.target.value as any })}
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
        <label className="text-xs text-gray-400">Top K Results ({settings.rag.top_k})</label>
        <input
          type="range"
          min="1"
          max="20"
          value={settings.rag.top_k}
          onChange={(e) => settings.updateRAG({ top_k: parseInt(e.target.value) || 5 })}
          className="w-24 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
        />
      </div>
    </div>
  );
}
