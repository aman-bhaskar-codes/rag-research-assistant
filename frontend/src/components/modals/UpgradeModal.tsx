"use client";

import { useSettingsStore } from "@/features/settings/store";
import { useUIStore } from "@/stores/ui-store";

export default function UpgradeModal() {
  const settings = useSettingsStore();
  const { closeModal } = useUIStore();

  return (
    <div className="space-y-6 text-left h-full flex flex-col items-center justify-center">
      <div className="text-center space-y-2 mb-6">
        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
          Upgrade to Premium
        </h2>
        <p className="text-sm text-gray-400 max-w-sm mx-auto">Unlock advanced intelligence algorithms and full RAG customization.</p>
      </div>

      <div className="bg-[#0B0F17] border border-gray-800 rounded-2xl p-8 shadow-inner relative overflow-hidden w-full max-w-sm">
        {/* Glow effect */}
        <div className="absolute top-0 right-0 -mt-4 -mr-4 w-32 h-32 bg-purple-500/10 blur-2xl rounded-full pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 -mb-4 -ml-4 w-32 h-32 bg-blue-500/10 blur-2xl rounded-full pointer-events-none"></div>

        <div className="flex items-end gap-2 mb-8">
          <span className="text-4xl font-bold text-white">$20</span>
          <span className="text-sm text-gray-400 mb-1">/ month</span>
        </div>

        <ul className="space-y-4 text-sm text-gray-300 font-medium mb-10 w-full text-left">
          <li className="flex items-center gap-3">
            <span className="text-green-400">✓</span> Full access to <span className="text-white font-bold ml-1">Gemini Pro</span>
          </li>
          <li className="flex items-center gap-3">
            <span className="text-green-400">✓</span> Visual Memory & Auto-Summary
          </li>
          <li className="flex items-center gap-3">
            <span className="text-green-400">✓</span> Advanced RAG Tuning (Reranking)
          </li>
          <li className="flex items-center gap-3">
            <span className="text-green-400">✓</span> Priority API latency
          </li>
        </ul>

        <button
          onClick={() => {
            // Note: Simulated Stripe Checkout
            settings.updateSettings({ plan: "premium" });
            closeModal();
          }}
          className="w-full bg-white hover:bg-gray-100 text-black py-3 rounded-xl font-bold transition-transform hover:scale-[1.02] shadow-[0_0_20px_rgba(255,255,255,0.1)] relative z-10"
        >
          {settings.plan === "premium" ? "Already Premium" : "Subscribe Now"}
        </button>
      </div>
      
      <p className="text-xs text-center text-gray-500 mt-4">
        Payments processed securely via Stripe. Cancel anytime.
      </p>
    </div>
  );
}
