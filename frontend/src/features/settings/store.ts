import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Settings, RAGConfig, MemoryConfig } from "./types";
import { DEFAULT_SETTINGS } from "@/config/constants";

// ─── Settings Store ──────────────────────────────────────────────────────────

interface SettingsState extends Settings {
  /** Update one or more settings fields */
  updateSettings: (partial: Partial<Settings>) => void;
  /** Update RAG config */
  updateRAG: (partial: Partial<RAGConfig>) => void;
  /** Update memory config */
  updateMemory: (partial: Partial<MemoryConfig>) => void;
  /** Reset all settings to defaults */
  resetSettings: () => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      ...DEFAULT_SETTINGS,

      updateSettings: (partial) => set((s) => ({ ...s, ...partial })),

      updateRAG: (partial) =>
        set((s) => ({ rag: { ...s.rag, ...partial } })),

      updateMemory: (partial) =>
        set((s) => ({ memory: { ...s.memory, ...partial } })),

      resetSettings: () => set({ ...DEFAULT_SETTINGS }),
    }),
    {
      name: "rag-assistant-settings",
    }
  )
);
