"use client";

import { useModeStore } from "@/features/modes/store";
import { MODE_CONFIG } from "@/features/modes/config";
import { Mode } from "@/features/modes/types";
import { motion } from "framer-motion";

const modes: Mode[] = ["ai_research", "programming", "business"];

export default function ModeSelector() {
  const { mode, setMode } = useModeStore();

  return (
    <div className="relative flex bg-[#111827] p-1 rounded-xl w-fit border border-gray-800/50 shadow-inner">
      <motion.div
        layout
        className={`absolute top-1 bottom-1 rounded-lg bg-gradient-to-r ${MODE_CONFIG[mode].color} shadow-md z-0`}
        style={{
          width: "33.33%",
          left: mode === "ai_research" ? "0%" : mode === "programming" ? "33.33%" : "66.66%",
        }}
        transition={{ type: "spring", stiffness: 400, damping: 30 }}
      />

      {modes.map((m) => {
        const config = MODE_CONFIG[m];
        const isSelected = mode === m;
        const isDisabled = 'disabled' in config && config.disabled;

        return (
          <button
            key={m}
            onClick={() => !isDisabled && setMode(m)}
            disabled={isDisabled}
            className={`relative z-10 px-4 py-1.5 text-[10px] font-bold tracking-tight transition-all duration-300 w-32 text-center flex flex-col items-center justify-center gap-0.5 ${
              isSelected 
                ? "text-white scale-105" 
                : isDisabled 
                  ? "text-gray-600 cursor-not-allowed opacity-60 grayscale bg-gray-900/40" 
                  : "text-gray-400 hover:text-gray-200"
            }`}
          >
            <span className="flex items-center gap-1.5">
              {isDisabled && <span className="text-[8px]">🔒</span>}
              {config.label}
            </span>
            {isDisabled && config.badge && (
              <span className="text-[7px] bg-red-500/10 text-red-500/80 px-1 py-0.5 rounded border border-red-500/20 uppercase tracking-tighter scale-90 -mt-0.5">
                {config.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
