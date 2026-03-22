import { create } from "zustand";
import { Mode } from "./types";
import { MODE_CONFIG } from "./config";

type ModeState = {
  mode: Mode;
  setMode: (m: Mode) => void;
};

export const useModeStore = create<ModeState>((set) => ({
  mode: "ai_research",

  setMode: (mode) => {
    // 🛡️ Lock: Prevent selecting disabled modes
    const config = MODE_CONFIG[mode as keyof typeof MODE_CONFIG];
    if (config && 'disabled' in config && config.disabled) {
      console.warn(`Mode ${mode} is currently disabled.`);
      return;
    }

    if (typeof window !== "undefined") {
      localStorage.setItem("rag_mode", mode);
    }
    set({ mode });
  },
}));
