"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sidebar } from "@/components/Sidebar";
import { SearchBar, SearchBarHandle } from "@/components/SearchBar";
import { StreamingAnswer } from "@/components/StreamingAnswer";
import { useStore } from "@/lib/store";

const SUGGESTIONS = [
  { icon: "🔬", text: "How does RAG retrieval work?" },
  { icon: "💻", text: "Explain transformers architecture" },
  { icon: "🌍", text: "Latest advances in renewable energy" },
  { icon: "🧠", text: "How to implement attention mechanisms?" },
];

export default function Home() {
  const [hasSearched, setHasSearched] = useState(false);
  const { currentTurns, sidebarOpen } = useStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  const searchBarRef = useRef<SearchBarHandle>(null);

  useEffect(() => { if (currentTurns.length > 0) setHasSearched(true); }, [currentTurns]);
  useEffect(() => {
    if (hasSearched) {
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
    }
  }, [currentTurns, hasSearched]);

  const handleRelatedClick = (q: string) => {
    // Directly submit the follow-up question
    searchBarRef.current?.submitQuery(q);
  };

  const handleSuggestionClick = (text: string) => {
    setHasSearched(true);
    searchBarRef.current?.submitQuery(text);
  };

  return (
    <div className="min-h-screen bg-plex-bg flex">
      <Sidebar />
      <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? "ml-64" : "ml-8"}`}>
        <div className="max-w-4xl mx-auto px-6 py-8">
          <AnimatePresence>
            {!hasSearched && (
              <motion.div initial={{ opacity: 1 }} exit={{ opacity: 0, y: -20 }} className="flex flex-col items-center justify-center min-h-[50vh] text-center mb-10">
                <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: 0.1 }}>
                  <div className="w-16 h-16 bg-plex-accent rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-plex-accent/20">
                    <span className="text-black font-bold text-2xl">P</span>
                  </div>
                  <h1 className="text-4xl font-bold text-plex-text mb-3">Where knowledge begins</h1>
                  <p className="text-plex-muted text-lg mb-10">Ask anything. Powered by Ollama + pgvector.</p>
                </motion.div>
                <div className="grid grid-cols-2 gap-3 w-full max-w-2xl mb-10">
                  {SUGGESTIONS.map((s, i) => (
                    <motion.button key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 + i * 0.07 }}
                      onClick={() => handleSuggestionClick(s.text)}
                      className="flex items-center gap-3 p-4 bg-plex-surface hover:bg-plex-hover border border-plex-border rounded-xl text-left transition-all group hover:border-plex-accent/30">
                      <span className="text-xl">{s.icon}</span>
                      <span className="text-sm text-plex-text group-hover:text-plex-accent transition-colors line-clamp-2">{s.text}</span>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          {hasSearched && <div className="mb-10"><StreamingAnswer onRelatedClick={handleRelatedClick} /></div>}
          <div ref={bottomRef} />
          <div className={hasSearched ? "sticky bottom-6 mt-6" : ""}>
            <SearchBar ref={searchBarRef} placeholder={hasSearched ? "Ask a follow-up..." : "Ask anything..."} onSearchStart={() => setHasSearched(true)} />
          </div>
        </div>
      </main>
    </div>
  );
}
