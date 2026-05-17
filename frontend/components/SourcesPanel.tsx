"use client";
import { motion, AnimatePresence } from "framer-motion";
import { FileText } from "lucide-react";
import { Source } from "@/lib/store";

function getFavicon(url: string): string {
  try {
    return `https://www.google.com/s2/favicons?domain=${new URL(url).hostname}&sz=32`;
  } catch {
    return "";
  }
}

function getDomain(url: string): string {
  try { return new URL(url).hostname.replace("www.", ""); }
  catch { return url; }
}

export function SourcesPanel({ sources, isLoading }: { sources: Source[]; isLoading?: boolean }) {
  if (!sources.length && !isLoading) return null;

  return (
    <div className="mb-6">
      <h3 className="text-xs font-semibold text-plex-muted uppercase tracking-wider mb-3">
        Sources
      </h3>

      {isLoading && !sources.length && (
        <div className="grid grid-cols-2 gap-2">
          {[1,2,3,4].map(i => (
            <div key={i} className="h-16 bg-plex-surface rounded-xl animate-pulse" />
          ))}
        </div>
      )}

      <AnimatePresence>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {sources.map((source, i) => (
            <motion.a
              key={source.index}
              href={source.url || "#"}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="group flex items-start gap-3 p-3 bg-plex-surface hover:bg-plex-hover rounded-xl border border-plex-border hover:border-plex-accent/30 transition-all cursor-pointer"
            >
              <div className="shrink-0 mt-0.5">
                {source.type === "web" && source.url ? (
                  <img
                    src={getFavicon(source.url)}
                    alt=""
                    className="w-5 h-5 rounded"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
                  />
                ) : (
                  <FileText className="w-5 h-5 text-plex-accent" />
                )}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-1">
                  <p className="text-sm font-medium text-plex-text line-clamp-1 group-hover:text-plex-accent transition-colors">
                    {source.title || getDomain(source.url)}
                  </p>
                  <span className="shrink-0 text-[10px] font-bold text-black bg-plex-accent rounded px-1 py-0.5">
                    [{source.index}]
                  </span>
                </div>
                <p className="text-xs text-plex-muted line-clamp-1 mt-0.5">
                  {source.url ? getDomain(source.url) : "Document"}
                </p>
              </div>
            </motion.a>
          ))}
        </div>
      </AnimatePresence>
    </div>
  );
}
