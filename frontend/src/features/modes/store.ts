import { create } from "zustand";
import { Mode } from "./types";

type ModeState = {
  mode: Mode;
  setMode: (m: Mode) => void;
};

export const useModeStore = create<ModeState>((set) => ({
  mode: "ai_research",

  setMode: (mode) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("rag_mode", mode);
    }
    set({ mode });
  },
}));
