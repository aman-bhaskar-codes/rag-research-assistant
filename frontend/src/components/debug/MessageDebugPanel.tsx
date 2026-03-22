"use client";

import { useUIStore } from "@/stores/ui-store";
import { Database } from "lucide-react";

export default function MessageDebugPanel({ data }: { data: any }) {
  const { debugMode } = useUIStore();

  if (!debugMode || !data) return null;

  return (
    <div className="mt-4 p-3 bg-[#020617] border border-gray-800/80 rounded-xl text-xs space-y-3 shadow-inner font-mono text-gray-400">
      <div className="flex items-center gap-1.5 text-cyan-500 font-semibold tracking-wider uppercase border-b border-gray-800/80 pb-2">
        <Database className="w-3.5 h-3.5" /> RAG Diagnostics
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
           <span className="text-gray-500">Mode:</span> <span className="text-purple-400">{data.mode || "unknown"}</span>
        </div>
        <div>
           <span className="text-gray-500">Model:</span> <span className="text-blue-400">{data.model || "unknown"}</span>
        </div>
        <div>
           <span className="text-gray-500">Latency:</span> <span className="text-orange-400">{data.latency || 0}ms</span>
        </div>
        <div>
           <span className="text-gray-500">Strategy:</span> <span className="text-green-400">{data.strategy || "hybrid"}</span>
        </div>
      </div>

      {data.chunks && data.chunks.length > 0 && (
        <div className="pt-2 border-t border-gray-800/50">
          <div className="text-gray-500 mb-2 uppercase tracking-tighter text-[10px]">Retrieved Context Chunks</div>
          <div className="space-y-1.5">
            {data.chunks.map((c: any, i: number) => (
              <div key={i} className="flex items-center justify-between gap-2 bg-[#1E293B]/30 p-1.5 rounded-lg border border-gray-800/40">
                <span className="truncate flex-1 text-gray-300" title={c.content}>{c.title || `Chunk ${i+1}`}</span>
                {c.score !== undefined && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${c.score > 0.7 ? "bg-green-500/10 text-green-500" : "bg-gray-500/10 text-gray-500"}`}>
                    {(c.score * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
