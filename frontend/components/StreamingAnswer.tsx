"use client";
import { motion } from "framer-motion";
import { AnswerBlock } from "./AnswerBlock";
import { SourcesPanel } from "./SourcesPanel";
import { useStore } from "@/lib/store";

export function StreamingAnswer({ onRelatedClick }: { onRelatedClick: (q: string) => void }) {
  const { currentTurns, streamingAnswer, currentSources, isLoading } = useStore();
  if (!currentTurns.length && !streamingAnswer && !isLoading) return null;
  return (
    <div className="max-w-3xl mx-auto">
      {currentTurns.map((turn) => (
        <div key={turn.id} className="mb-10">
          <SourcesPanel sources={turn.sources} />
          <AnswerBlock query={turn.query} answer={turn.answer} sources={turn.sources} relatedQuestions={turn.relatedQuestions} model={turn.model} isStreaming={false} onRelatedClick={onRelatedClick} />
        </div>
      ))}
      {(streamingAnswer || isLoading) && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <SourcesPanel sources={currentSources} isLoading={isLoading && !currentSources.length} />
          {streamingAnswer && <AnswerBlock query="" answer={streamingAnswer} sources={currentSources} relatedQuestions={[]} model="" isStreaming={true} />}
          {isLoading && !streamingAnswer && (
            <div className="flex gap-2 py-4">
              {[0,1,2].map(i => (<div key={i} className="w-2 h-2 bg-plex-accent rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
