import { create } from "zustand";

// ─── UI Store ────────────────────────────────────────────────────────────────

export type ModalType = "settings" | "profile" | "memory" | "upgrade" | "upload" | null;

interface UIState {
  sidebarOpen: boolean;
  debugMode: boolean;
  sourcePanelOpen: boolean;
  settingsPanelOpen: boolean;
  uploadModalOpen: boolean;
  activeModal: ModalType;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleDebug: () => void;
  toggleSourcePanel: () => void;
  toggleSettingsPanel: () => void;
  toggleUploadModal: () => void;
  openModal: (modal: ModalType) => void;
  closeModal: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  debugMode: false,
  sourcePanelOpen: false,
  settingsPanelOpen: false,
  uploadModalOpen: false,
  activeModal: null,

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleDebug: () => set((s) => ({ debugMode: !s.debugMode })),
  toggleSourcePanel: () => set((s) => ({ sourcePanelOpen: !s.sourcePanelOpen })),
  toggleSettingsPanel: () =>
    set((s) => ({ settingsPanelOpen: !s.settingsPanelOpen })),
  toggleUploadModal: () =>
    set((s) => ({ uploadModalOpen: !s.uploadModalOpen })),
  openModal: (modal) => set({ activeModal: modal }),
  closeModal: () => set({ activeModal: null }),
}));
