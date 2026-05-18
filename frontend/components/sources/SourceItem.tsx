"use client";

import { Source } from "@/features/chat/types";

export default function SourceItem({ source }: { source: Source }) {
  return (
    <div className="p-3 rounded-lg bg-[#020617] border border-gray-800 hover:border-gray-600 transition text-left">
      <div className="text-xs text-gray-400 mb-1 font-medium truncate">
        {source.title || "Source"}
      </div>

      <div className="text-sm text-gray-200 line-clamp-3">
        {source.content}
      </div>

      {source.score !== undefined && (
        <div className="text-[10px] text-gray-500 mt-2">
          Score: {source.score.toFixed(2)}
        </div>
      )}
    </div>
  );
}
