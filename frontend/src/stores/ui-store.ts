import { create } from "zustand";

// ─── UI Store ────────────────────────────────────────────────────────────────

interface UIState {
  sidebarOpen: boolean;
  debugMode: boolean;
  sourcePanelOpen: boolean;
  settingsPanelOpen: boolean;
  uploadModalOpen: boolean;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleDebug: () => void;
  toggleSourcePanel: () => void;
  toggleSettingsPanel: () => void;
  toggleUploadModal: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  debugMode: false,
  sourcePanelOpen: false,
  settingsPanelOpen: false,
  uploadModalOpen: false,

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleDebug: () => set((s) => ({ debugMode: !s.debugMode })),
  toggleSourcePanel: () => set((s) => ({ sourcePanelOpen: !s.sourcePanelOpen })),
  toggleSettingsPanel: () =>
    set((s) => ({ settingsPanelOpen: !s.settingsPanelOpen })),
  toggleUploadModal: () =>
    set((s) => ({ uploadModalOpen: !s.uploadModalOpen })),
}));
