"use client";

import { Source } from "@/features/chat/types";

export default function SourceCard({ source, index }: { source: Source; index: number }) {
  return (
    <div className="flex flex-col gap-1 p-3 rounded-xl bg-[#0F172A] border border-gray-800 hover:border-gray-700 transition-colors text-left group">
      <div className="flex items-center justify-between gap-4">
        <span className="text-xs font-semibold text-gray-300 w-full truncate">
          <span className="text-blue-500 mr-1">[{index + 1}]</span>
          {source.title || "Unknown Document"}
        </span>
        {source.score !== undefined && (
          <span className="text-[10px] text-gray-500 shrink-0">
            {(source.score * 100).toFixed(0)}%
          </span>
        )}
      </div>
      <p className="text-xs text-gray-400 line-clamp-3 group-hover:line-clamp-none transition-all">
        {source.content}
      </p>
    </div>
  );
}
