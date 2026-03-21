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

      {modes.map((m) => (
        <button
          key={m}
          onClick={() => setMode(m)}
          className={`relative z-10 px-4 py-1.5 text-xs font-semibold transition-colors duration-200 w-28 text-center flex items-center justify-center ${
            mode === m ? "text-white shadow-sm" : "text-gray-400 hover:text-gray-200"
          }`}
        >
          {MODE_CONFIG[m].label}
        </button>
      ))}
    </div>
  );
}
