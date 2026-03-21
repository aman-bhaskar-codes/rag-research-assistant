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
           <span className="text-gray-500">Model:</span> <span className="text-blue-400">{data.model || "unknown"}</span>
        </div>
        <div>
           <span className="text-gray-500">Latency:</span> <span className="text-orange-400">{data.latency || 0}ms</span>
        </div>
        <div className="col-span-2">
           <span className="text-gray-500">Retrieval Pipeline:</span> <span className="text-green-400">{data.strategy || "hybrid"}</span>
        </div>
      </div>

      {data.chunks && data.chunks.length > 0 && (
        <div className="pt-2 border-t border-gray-800/50">
          <div className="text-gray-500 mb-1">Extracted Chunks:</div>
          <ul className="list-disc ml-5 space-y-1 text-gray-500">
            {data.chunks.map((c: any, i: number) => (
              <li key={i} className="truncate max-w-[90%] hover:text-gray-300 transition-colors cursor-help" title={c}>{c.slice(0, 80)}...</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
