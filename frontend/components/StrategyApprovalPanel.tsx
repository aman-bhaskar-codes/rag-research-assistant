"use client";
import { useEffect, useState } from "react";
import { Check, X, Lightbulb } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface PendingStrategy {
  id: string;
  trigger: string;
  strategy: string;
  source: string;
  created_at: string;
}

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function StrategyApprovalPanel() {
  const [pending, setPending] = useState<PendingStrategy[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPending = () => {
    fetch(`${API}/agent/strategies/pending`)
      .then(r => r.json())
      .then(d => { setPending(d.pending || []); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(fetchPending, []);

  const approve = async (id: string) => {
    await fetch(`${API}/agent/strategies/${id}/approve`, { method: "POST" });
    setPending(prev => prev.filter(s => s.id !== id));
  };

  const dismiss = (id: string) => {
    setPending(prev => prev.filter(s => s.id !== id));
  };

  if (loading) return (
    <div className="mb-6 p-4 rounded-xl border border-plex-border bg-plex-surface animate-pulse">
      <div className="h-4 bg-plex-muted/20 w-1/3 rounded mb-2"></div>
      <div className="h-10 bg-plex-muted/10 w-full rounded"></div>
    </div>
  );
  if (!pending.length) return null;

  return (
    <div className="mb-6">
      <h3 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-3 flex items-center gap-2">
        <Lightbulb className="w-3.5 h-3.5" />
        Strategy Proposals ({pending.length}) — Approve to activate
      </h3>

      <AnimatePresence>
        {pending.map(strategy => (
          <motion.div
            key={strategy.id}
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className="mb-3 p-4 bg-amber-500/5 border border-amber-500/20 rounded-xl"
          >
            <p className="text-xs font-medium text-amber-400 mb-1">When: {strategy.trigger}</p>
            <p className="text-xs text-plex-text whitespace-pre-wrap font-mono bg-plex-bg rounded-lg p-2 mb-3">
              {strategy.strategy}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => approve(strategy.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg text-xs font-medium transition-colors"
              >
                <Check className="w-3.5 h-3.5" /> Approve
              </button>
              <button
                onClick={() => dismiss(strategy.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg text-xs font-medium transition-colors"
              >
                <X className="w-3.5 h-3.5" /> Dismiss
              </button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
