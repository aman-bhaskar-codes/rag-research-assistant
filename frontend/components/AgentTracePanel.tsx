"use client";
/**
 * Real-time agent trace visualization — shows the agent's thinking step by step.
 * Perplexity-style but for the agent: each step shows action, reasoning, result.
 */
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Search, BookOpen, FileText, CheckCircle, XCircle, Loader2, ChevronDown } from "lucide-react";

export interface AgentStep {
  step: number;
  action: string;
  reasoning: string;
  result_preview: string;
  success: boolean;
  step_score: number;
  latency_ms: number;
}

interface AgentTracePanelProps {
  steps: AgentStep[];
  isRunning: boolean;
  currentAction?: string;
  qualityScore?: number;
  totalSteps?: number;
  driftDetected?: boolean;
}

const ACTION_ICONS: Record<string, React.ReactNode> = {
  "search_knowledge_base": <BookOpen className="w-3.5 h-3.5" />,
  "web_search":            <Search className="w-3.5 h-3.5" />,
  "arxiv_search":          <FileText className="w-3.5 h-3.5" />,
  "wikipedia_search":      <FileText className="w-3.5 h-3.5" />,
  "write_note":            <Brain className="w-3.5 h-3.5" />,
  "read_notes":            <Brain className="w-3.5 h-3.5" />,
  "finish":                <CheckCircle className="w-3.5 h-3.5" />,
};

const ACTION_COLORS: Record<string, string> = {
  "search_knowledge_base": "text-purple-400",
  "web_search":            "text-blue-400",
  "arxiv_search":          "text-amber-400",
  "wikipedia_search":      "text-green-400",
  "write_note":            "text-plex-accent",
  "finish":                "text-green-400",
};

function ScoreBar({ score }: { score: number }) {
  const color = score >= 0.7 ? "bg-green-500" : score >= 0.45 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 bg-plex-border rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${score * 100}%` }} />
      </div>
      <span className="text-[10px] text-plex-muted">{(score * 100).toFixed(0)}%</span>
    </div>
  );
}

function StepCard({ step, index }: { step: AgentStep; index: number }) {
  const [expanded, setExpanded] = useState(false);
  const actionColor = ACTION_COLORS[step.action] || "text-plex-muted";
  const icon = ACTION_ICONS[step.action] || <Brain className="w-3.5 h-3.5" />;

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="border border-plex-border rounded-xl overflow-hidden"
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-3 bg-plex-surface hover:bg-plex-hover transition-colors text-left"
      >
        <span className="text-xs text-plex-muted w-5 shrink-0 font-mono">{step.step}</span>

        <span className={`shrink-0 ${actionColor}`}>{icon}</span>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={`text-xs font-mono font-medium ${actionColor}`}>{step.action}</span>
            <ScoreBar score={step.step_score} />
          </div>
          <p className="text-xs text-plex-muted line-clamp-1 mt-0.5">{step.reasoning}</p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {step.success
            ? <CheckCircle className="w-3.5 h-3.5 text-green-500" />
            : <XCircle className="w-3.5 h-3.5 text-red-500" />
          }
          <span className="text-[10px] text-plex-subtle">{step.latency_ms.toFixed(0)}ms</span>
          <ChevronDown className={`w-3.5 h-3.5 text-plex-muted transition-transform ${expanded ? "rotate-180" : ""}`} />
        </div>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: "auto" }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-3 bg-plex-bg border-t border-plex-border">
              <p className="text-xs text-plex-muted mt-2 mb-1 font-semibold">REASONING</p>
              <p className="text-xs text-plex-text font-mono">{step.reasoning}</p>
              <p className="text-xs text-plex-muted mt-2 mb-1 font-semibold">RESULT</p>
              <p className="text-xs text-plex-text font-mono whitespace-pre-wrap">{step.result_preview}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function AgentTracePanel({
  steps, isRunning, currentAction, qualityScore, totalSteps, driftDetected
}: AgentTracePanelProps) {
  if (!steps.length && !isRunning) return null;

  return (
    <div className="mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-plex-muted uppercase tracking-wider flex items-center gap-2">
          <Brain className="w-3.5 h-3.5 text-plex-accent" />
          Agent Reasoning
          {isRunning && <Loader2 className="w-3 h-3 animate-spin text-plex-accent" />}
        </h3>
        {qualityScore !== undefined && !isRunning && (
          <div className="flex items-center gap-2">
            <ScoreBar score={qualityScore} />
            <span className="text-xs text-plex-muted">{totalSteps} steps</span>
          </div>
        )}
      </div>

      {/* Drift warning */}
      {driftDetected && (
        <div className="mb-3 p-2 bg-amber-500/10 border border-amber-500/30 rounded-lg text-xs text-amber-400">
          ⚠️ Goal drift detected — agent self-correcting
        </div>
      )}

      {/* Current action (streaming) */}
      {isRunning && currentAction && (
        <div className="flex items-center gap-2 p-3 bg-plex-surface rounded-xl border border-plex-accent/30 mb-2 animate-pulse">
          <Loader2 className="w-3.5 h-3.5 text-plex-accent animate-spin" />
          <span className="text-xs text-plex-accent font-mono">{currentAction}</span>
        </div>
      )}

      {/* Steps */}
      <div className="space-y-2">
        {steps.map((step, i) => (
          <StepCard key={step.step} step={step} index={i} />
        ))}
      </div>
    </div>
  );
}
