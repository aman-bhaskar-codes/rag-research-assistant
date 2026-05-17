"use client";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, ThumbsUp, ThumbsDown } from "lucide-react";
import { Source } from "@/lib/store";

interface Props {
  query: string;
  answer: string;
  sources: Source[];
  relatedQuestions: string[];
  model: string;
  isStreaming?: boolean;
  onRelatedClick?: (q: string) => void;
  onFeedback?: (v: 1 | -1) => void;
}

export function AnswerBlock({ query, answer, sources, relatedQuestions, model, isStreaming, onRelatedClick, onFeedback }: Props) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
      {query && <h2 className="text-xl font-semibold text-plex-text mb-4">{query}</h2>}
      <div className="markdown-answer">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{answer}</ReactMarkdown>
        {isStreaming && <span className="inline-block w-2 h-4 bg-plex-accent animate-pulse rounded-sm ml-0.5" />}
      </div>
      {!isStreaming && (
        <div className="flex items-center gap-3 mt-4 pt-4 border-t border-plex-border">
          <button onClick={() => navigator.clipboard.writeText(answer)} className="flex items-center gap-1.5 text-xs text-plex-muted hover:text-plex-text transition-colors"><Copy className="w-3.5 h-3.5" /> Copy</button>
          <button onClick={() => onFeedback?.(1)} className="text-xs text-plex-muted hover:text-green-400"><ThumbsUp className="w-3.5 h-3.5" /></button>
          <button onClick={() => onFeedback?.(-1)} className="text-xs text-plex-muted hover:text-red-400"><ThumbsDown className="w-3.5 h-3.5" /></button>
          <span className="ml-auto text-xs text-plex-subtle">{model}</span>
        </div>
      )}
      {!isStreaming && relatedQuestions.length > 0 && (
        <div className="mt-6">
          <h4 className="text-xs font-semibold text-plex-muted uppercase tracking-wider mb-3">Related</h4>
          <div className="space-y-2">
            {relatedQuestions.map((q, i) => (
              <motion.button key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.08 }}
                onClick={() => onRelatedClick?.(q)}
                className="w-full flex items-center gap-3 p-3 text-left bg-plex-surface hover:bg-plex-hover rounded-xl border border-plex-border transition-all group">
                <span className="text-plex-accent">→</span>
                <span className="text-sm text-plex-text group-hover:text-plex-accent">{q}</span>
              </motion.button>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
