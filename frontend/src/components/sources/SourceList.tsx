"use client";

import { Source } from "@/features/chat/types";
import SourceItem from "./SourceItem";

export default function SourceList({ sources }: { sources: Source[] }) {
  if (!sources?.length) return null;

  return (
    <div className="mt-3 space-y-2 opacity-80 hover:opacity-100 transition-opacity">
      <div className="text-xs text-gray-400 uppercase tracking-wide font-semibold mb-2">
        Sources
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {sources.map((s, i) => (
          <SourceItem key={i} source={s} />
        ))}
      </div>
    </div>
  );
}
