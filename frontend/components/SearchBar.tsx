"use client";
import { useState, useRef, KeyboardEvent, useImperativeHandle, forwardRef } from "react";
import { Search, ArrowRight, Globe, BookOpen, Loader2 } from "lucide-react";
import { useStore } from "@/lib/store";
import { FOCUS_MODES } from "@/lib/focus";
import { streamSearch } from "@/lib/stream";
import { v4 as uuidv4 } from "uuid";

export interface SearchBarHandle {
  submitQuery: (q: string) => void;
}

interface SearchBarProps {
  placeholder?: string;
  onSearchStart?: () => void;
}

export const SearchBar = forwardRef<SearchBarHandle, SearchBarProps>(
  function SearchBar({ placeholder = "Ask anything...", onSearchStart }, ref) {
    const [query, setQuery] = useState("");
    const abortRef = useRef<AbortController | null>(null);

    const store = useStore();
    const {
      sessionId, selectedModel, focusMode, useWeb, useRag, isLoading,
      setSources, appendToken, finaliseAnswer, resetStream, setLoading,
      currentTurns,
    } = store;

    const doSearch = async (q: string) => {
      if (!q.trim() || isLoading) return;

      setQuery("");
      onSearchStart?.();
      setLoading(true);
      resetStream();

      if (abortRef.current) abortRef.current.abort();
      abortRef.current = new AbortController();

      const turnId = uuidv4();
      let sources: any[] = [];
      let relatedQuestions: string[] = [];
      let answer = "";

      await streamSearch(
        { query: q, sessionId, focusMode, model: selectedModel, useWeb, useRag },
        {
          onSources: (s) => {
            sources = s;
            setSources(s);
          },
          onToken: (t) => {
            answer += t;
            appendToken(t);
          },
          onRelated: (r) => { relatedQuestions = r; },
          onDone: (meta: any) => {
            finaliseAnswer({
              id: meta.turn_id || turnId,
              query: q,
              answer,
              sources,
              relatedQuestions,
              model: selectedModel,
              focusMode,
            });
            store.addHistorySession({
              id: meta.session_id || sessionId,
              title: q.slice(0, 60),
              lastQuery: q,
              createdAt: new Date().toISOString(),
              turnCount: currentTurns.length + 1,
            });
          },
          onError: (e) => {
            resetStream();
            console.error("Search error:", e);
          },
        },
        abortRef.current.signal
      );
    };

    // Expose submitQuery to parent
    useImperativeHandle(ref, () => ({
      submitQuery: (q: string) => doSearch(q),
    }));

    const handleSearch = () => doSearch(query.trim());

    const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSearch();
      }
    };

    const focusConfig = FOCUS_MODES.find(f => f.id === focusMode);

    return (
      <div className="w-full max-w-3xl mx-auto">
        <div className="flex gap-2 mb-3 flex-wrap">
          {FOCUS_MODES.map((mode) => (
            <button
              key={mode.id}
              onClick={() => store.setFocusMode(mode.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                focusMode === mode.id
                  ? "bg-plex-accent text-black"
                  : "bg-plex-surface text-plex-muted hover:bg-plex-hover hover:text-plex-text border border-plex-border"
              }`}
            >
              <span>{mode.icon}</span>
              {mode.label}
            </button>
          ))}
        </div>

        <div className="relative bg-plex-surface border border-plex-border rounded-2xl p-4 focus-within:border-plex-accent transition-colors">
          <div className="flex items-start gap-3">
            <Search className="w-5 h-5 text-plex-muted mt-0.5 shrink-0" />
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={onKey}
              placeholder={placeholder}
              className="flex-1 bg-transparent outline-none resize-none text-plex-text placeholder-plex-muted text-base leading-relaxed min-h-[24px] max-h-[160px]"
              rows={1}
              onInput={(e) => {
                const el = e.currentTarget;
                el.style.height = "auto";
                el.style.height = Math.min(el.scrollHeight, 160) + "px";
              }}
            />
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => store.setUseWeb(!useWeb)}
                title={useWeb ? "Web search ON" : "Web search OFF"}
                className={`p-2 rounded-lg transition-colors ${
                  useWeb ? "text-plex-accent bg-plex-accent/10" : "text-plex-subtle hover:text-plex-muted"
                }`}
              >
                <Globe className="w-4 h-4" />
              </button>
              <button
                onClick={() => store.setUseRag(!useRag)}
                title={useRag ? "Documents ON" : "Documents OFF"}
                className={`p-2 rounded-lg transition-colors ${
                  useRag ? "text-plex-accent bg-plex-accent/10" : "text-plex-subtle hover:text-plex-muted"
                }`}
              >
                <BookOpen className="w-4 h-4" />
              </button>
              <button
                onClick={handleSearch}
                disabled={!query.trim() || isLoading}
                className="p-2 bg-plex-accent rounded-lg text-black hover:bg-opacity-80 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                {isLoading
                  ? <Loader2 className="w-4 h-4 animate-spin" />
                  : <ArrowRight className="w-4 h-4" />
                }
              </button>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 mt-2 text-xs text-plex-muted">
          <span>{focusConfig?.icon} {focusConfig?.description}</span>
          <span>·</span>
          <span>{selectedModel}</span>
          {useWeb && <><span>·</span><Globe className="w-3 h-3" /><span>Web</span></>}
          {useRag && <><span>·</span><BookOpen className="w-3 h-3" /><span>Docs</span></>}
        </div>
      </div>
    );
  }
);
