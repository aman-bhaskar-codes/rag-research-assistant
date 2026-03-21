"use client";

import { useSettingsStore } from "@/features/settings/store";

export default function AccountSection() {
  const settings = useSettingsStore();

  return (
    <div className="space-y-4 pt-4 border-t border-gray-800">
      <div className="text-sm font-semibold mb-2 text-gray-300">Account</div>
      <div className="text-xs text-gray-400 mb-2 uppercase tracking-wide">
        Current Plan: <span className={settings.plan === "premium" ? "text-blue-400" : "text-gray-300"}>{settings.plan}</span>
      </div>

      {settings.plan !== "premium" && (
        <div 
          onClick={() => settings.updateSettings({ plan: "premium" })}
          className="p-3 bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-lg text-sm transition-all hover:border-purple-500/50 cursor-pointer"
        >
          <p className="text-gray-200 font-medium text-xs">Unlock Gemini Pro & advanced RAG precision.</p>
          <button className="block mt-2 text-xs text-blue-400 font-medium hover:underline flex items-center gap-1 w-full text-left">
            ✨ Upgrade to Premium
          </button>
        </div>
      )}
    </div>
  );
}
