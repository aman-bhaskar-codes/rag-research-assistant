"use client";
import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Play, Loader2 } from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { AgentTracePanel, AgentStep } from "@/components/AgentTracePanel";
import { CapabilityDashboard } from "@/components/CapabilityDashboard";
import { StrategyApprovalPanel } from "@/components/StrategyApprovalPanel";
import { useStore } from "@/lib/store";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MAX_STEPS = 10;

export default function AgentPage() {
  const [task, setTask] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [currentAction, setCurrentAction] = useState<string | undefined>();
  const [finalAnswer, setFinalAnswer] = useState<string | null>(null);
  const [qualityScore, setQualityScore] = useState<number | undefined>();
  const [driftDetected, setDriftDetected] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const { sidebarOpen, selectedModel, sessionId } = useStore();

  const handleRun = async () => {
    if (!task.trim() || isRunning) return;
    setIsRunning(true);
    setSteps([]);
    setFinalAnswer(null);
    setQualityScore(undefined);
    setDriftDetected(false);

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    try {
      const res = await fetch(`${API}/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task,
          session_id: sessionId,
          focus_mode: "research",
          model: selectedModel,
          max_steps: MAX_STEPS,
        }),
        signal: abortRef.current.signal,
      });

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let eventType = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            eventType = line.slice(7).trim();
          } else if (line.startsWith("data: ")) {
            const data = JSON.parse(line.slice(6).trim());
            switch (eventType) {
              case "agent_thinking":
                setCurrentAction(data.action);
                break;
              case "agent_step":
                setCurrentAction(undefined);
                setSteps(prev => [...prev, data as AgentStep]);
                break;
              case "drift_detected":
                setDriftDetected(true);
                setTimeout(() => setDriftDetected(false), 5000);
                break;
              case "final_answer":
                setFinalAnswer(data.answer);
                setQualityScore(data.quality);
                setIsRunning(false);
                break;
              case "error":
                setFinalAnswer(`Error: ${data.message}`);
                setIsRunning(false);
                break;
            }
          }
        }
      }
    } catch (e: unknown) {
      if (e instanceof Error && e.name !== "AbortError") {
        setFinalAnswer(`Connection error: ${e.message}`);
      } else if (!(e instanceof Error)) {
        setFinalAnswer(`Connection error: ${String(e)}`);
      }
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-plex-bg flex">
      <Sidebar />
      <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? "ml-64" : "ml-8"}`}>
        <div className="max-w-4xl mx-auto px-6 py-8">

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-plex-text mb-1">Research Agent</h1>
            <p className="text-plex-muted text-sm">
              Multi-step autonomous research with self-improving memory
            </p>
          </div>

          {/* Strategy approvals (if any) */}
          <StrategyApprovalPanel />

          {/* Task input */}
          <div className="mb-6 bg-plex-surface border border-plex-border rounded-2xl p-4">
            <textarea
              value={task}
              onChange={e => setTask(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleRun(); }}
              placeholder="Give the agent a research task... (Ctrl+Enter to run)"
              className="w-full bg-transparent outline-none resize-none text-plex-text placeholder-plex-muted text-sm leading-relaxed"
              rows={3}
            />
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-plex-border">
              <span className="text-xs text-plex-muted">
                Model: {selectedModel} · Max steps: {MAX_STEPS}
              </span>
              <button
                onClick={handleRun}
                disabled={!task.trim() || isRunning}
                className="flex items-center gap-2 px-4 py-2 bg-plex-accent rounded-xl text-black text-sm font-medium hover:bg-opacity-80 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                {isRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                {isRunning ? "Researching..." : "Run Agent"}
              </button>
            </div>
          </div>

          {/* Main content: traces + answer */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <AgentTracePanel
                steps={steps}
                isRunning={isRunning}
                currentAction={currentAction}
                qualityScore={qualityScore}
                totalSteps={steps.length}
                driftDetected={driftDetected}
              />

              {finalAnswer && (
                <motion.div
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-4 bg-plex-surface border border-plex-border rounded-xl"
                >
                  <h3 className="text-xs font-semibold text-plex-accent uppercase tracking-wider mb-3">
                    Research Answer
                  </h3>
                  <p className="text-sm text-plex-text whitespace-pre-wrap leading-relaxed">{finalAnswer}</p>
                </motion.div>
              )}
            </div>

            <div>
              <CapabilityDashboard />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
