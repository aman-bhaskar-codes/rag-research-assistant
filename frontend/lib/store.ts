import { create } from "zustand";
import { persist } from "zustand/middleware";
import { v4 as uuidv4 } from "uuid";

export interface Source {
  index: number;
  title: string;
  url: string;
  description: string;
  type: "web" | "document";
}

export interface SearchTurn {
  id: string;
  query: string;
  answer: string;
  sources: Source[];
  relatedQuestions: string[];
  model: string;
  focusMode: string;
}

export interface HistorySession {
  id: string;
  title: string;
  lastQuery: string | null;
  createdAt: string;
  turnCount: number;
}

interface AppState {
  sessionId: string;
  setSessionId: (id: string) => void;
  currentTurns: SearchTurn[];
  isLoading: boolean;
  currentSources: Source[];
  streamingAnswer: string;
  selectedModel: string;
  focusMode: string;
  useWeb: boolean;
  useRag: boolean;
  darkMode: boolean;
  sidebarOpen: boolean;
  history: HistorySession[];
  setModel: (model: string) => void;
  setFocusMode: (mode: string) => void;
  setUseWeb: (v: boolean) => void;
  setUseRag: (v: boolean) => void;
  toggleDark: () => void;
  toggleSidebar: () => void;
  setLoading: (v: boolean) => void;
  appendToken: (token: string) => void;
  setSources: (sources: Source[]) => void;
  finaliseAnswer: (turn: SearchTurn) => void;
  resetStream: () => void;
  addHistorySession: (session: HistorySession) => void;
  newSession: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      sessionId: uuidv4(),
      setSessionId: (id) => set({ sessionId: id }),

      currentTurns: [],
      isLoading: false,
      currentSources: [],
      streamingAnswer: "",

      selectedModel: "llama3.2:3b",
      focusMode: "general",
      useWeb: true,
      useRag: true,
      darkMode: true,
      sidebarOpen: true,
      history: [],

      setModel: (model) => set({ selectedModel: model }),
      setFocusMode: (mode) => set({ focusMode: mode }),
      setUseWeb: (v) => set({ useWeb: v }),
      setUseRag: (v) => set({ useRag: v }),
      toggleDark: () => set((s) => ({ darkMode: !s.darkMode })),
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setLoading: (v) => set({ isLoading: v }),

      appendToken: (token) =>
        set((s) => ({ streamingAnswer: s.streamingAnswer + token, isLoading: false })),

      setSources: (sources) => set({ currentSources: sources }),

      finaliseAnswer: (turn) =>
        set((s) => ({
          currentTurns: [...s.currentTurns, turn],
          streamingAnswer: "",
          currentSources: [],
          isLoading: false,
        })),

      resetStream: () =>
        set({ streamingAnswer: "", currentSources: [], isLoading: false }),

      addHistorySession: (session) =>
        set((s) => ({ history: [session, ...s.history.slice(0, 49)] })),

      newSession: () =>
        set({
          sessionId: uuidv4(),
          currentTurns: [],
          streamingAnswer: "",
          currentSources: [],
          isLoading: false,
        }),
    }),
    {
      name: "research-assistant-store",
      partialize: (s) => ({
        selectedModel: s.selectedModel,
        focusMode: s.focusMode,
        useWeb: s.useWeb,
        useRag: s.useRag,
        darkMode: s.darkMode,
        sidebarOpen: s.sidebarOpen,
        history: s.history,
      }),
    }
  )
);
