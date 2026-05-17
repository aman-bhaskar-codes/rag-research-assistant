"use client";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, History, Settings, ChevronLeft, ChevronRight, Cpu } from "lucide-react";
import { useStore } from "@/lib/store";

const MODELS = [
  { id: "llama3.2:3b", name: "Llama 3.2", badge: "Fast" },
  { id: "phi4-mini:latest", name: "Phi-4 Mini", badge: "Smart" },
  { id: "qwen2.5:3b", name: "Qwen 2.5", badge: "Multi" },
];

export function Sidebar() {
  const { sidebarOpen, toggleSidebar, history, newSession, selectedModel, setModel } = useStore();
  return (
    <>
      <button onClick={toggleSidebar} className="fixed left-0 top-4 z-50 w-8 h-8 flex items-center justify-center bg-plex-surface border border-plex-border rounded-r-lg hover:bg-plex-hover transition-colors">
        {sidebarOpen ? <ChevronLeft className="w-4 h-4 text-plex-muted" /> : <ChevronRight className="w-4 h-4 text-plex-muted" />}
      </button>
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside initial={{ x: -280 }} animate={{ x: 0 }} exit={{ x: -280 }} transition={{ type: "spring", damping: 25, stiffness: 200 }} className="fixed left-0 top-0 bottom-0 w-64 bg-plex-surface border-r border-plex-border z-40 flex flex-col">
            <div className="p-4 border-b border-plex-border">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 bg-plex-accent rounded-lg flex items-center justify-center"><span className="text-black font-bold text-sm">P</span></div>
                <span className="font-semibold text-plex-text">Perplexity</span>
              </div>
            </div>
            <div className="p-3">
              <button onClick={newSession} className="w-full flex items-center gap-2 px-3 py-2 rounded-xl bg-plex-accent/10 hover:bg-plex-accent/20 text-plex-accent text-sm font-medium transition-colors">
                <Plus className="w-4 h-4" /> New Search
              </button>
            </div>
            <div className="px-3 pb-3">
              <p className="text-xs text-plex-muted mb-2 flex items-center gap-1"><Cpu className="w-3 h-3" /> Model</p>
              <div className="space-y-1">
                {MODELS.map(m => (
                  <button key={m.id} onClick={() => setModel(m.id)} className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${selectedModel === m.id ? "bg-plex-accent/15 text-plex-accent" : "text-plex-muted hover:bg-plex-hover hover:text-plex-text"}`}>
                    <span>{m.name}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${selectedModel === m.id ? "bg-plex-accent text-black" : "bg-plex-border text-plex-muted"}`}>{m.badge}</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="border-t border-plex-border mx-3" />
            <div className="flex-1 overflow-y-auto p-3">
              <p className="text-xs text-plex-muted mb-2 flex items-center gap-1"><History className="w-3 h-3" /> Recent</p>
              {history.length === 0 ? <p className="text-xs text-plex-subtle text-center py-4">No searches yet</p> : (
                <div className="space-y-1">
                  {history.slice(0, 20).map(h => (
                    <div key={h.id} className="px-3 py-2 rounded-lg hover:bg-plex-hover cursor-pointer group">
                      <p className="text-sm text-plex-text line-clamp-1 group-hover:text-plex-accent transition-colors">{h.title}</p>
                      <p className="text-xs text-plex-subtle">{h.turnCount} turns</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="p-3 border-t border-plex-border">
              <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-plex-muted hover:bg-plex-hover hover:text-plex-text transition-colors">
                <Settings className="w-4 h-4" /> Settings
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}
