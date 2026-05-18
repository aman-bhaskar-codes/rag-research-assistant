"use client";

import { Source } from "@/features/chat/types";
import { motion } from "framer-motion";
import SourceItem from "./SourceItem";

export default function SourceList({ sources }: { sources: Source[] }) {
  if (!sources?.length) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      className="mt-3 space-y-2 opacity-80 hover:opacity-100 transition-opacity overflow-hidden"
    >
      <div className="text-xs text-gray-400 uppercase tracking-wide font-semibold mb-2">
        Sources
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {sources.map((s, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <SourceItem source={s} />
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
