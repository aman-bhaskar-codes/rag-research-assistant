// ─── API Configuration ───────────────────────────────────────────────────────

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

// ─── Default Settings ────────────────────────────────────────────────────────

export const DEFAULT_MODEL = "qwen";

export const DEFAULT_TEMPERATURE = 0.7;

export const DEFAULT_SETTINGS = {
  model: DEFAULT_MODEL,
  temperature: DEFAULT_TEMPERATURE,
  rag: {
    strategy: "hybrid" as const,
    top_k: 5,
    rerank: true,
  },
  memory: {
    enabled: true,
  },
  plan: "free",
} as const;

// ─── Model Options ───────────────────────────────────────────────────────────

export const MODEL_OPTIONS = [
  { value: "phi3:mini", label: "phi3:mini", tier: "free" },
  { value: "gemma:2b", label: "gemma:2b", tier: "free" },
  { value: "qwen2.5:3b", label: "qwen2.5:3b", tier: "free" },
  { value: "mistral", label: "mistral", tier: "free+" },
  { value: "gemini-pro", label: "gemini-pro", tier: "premium" },
] as const;

// ─── RAG Strategy Options ────────────────────────────────────────────────────

export const RAG_STRATEGIES = [
  { value: "hybrid", label: "Hybrid (Semantic + Keyword)" },
  { value: "semantic", label: "Semantic Only" },
  { value: "keyword", label: "Keyword Only" },
] as const;

// ─── Streaming ───────────────────────────────────────────────────────────────

export const STREAM_DONE_SIGNAL = "[DONE]";

// ─── UI ──────────────────────────────────────────────────────────────────────

export const MAX_MESSAGE_LENGTH = 4000;
export const SIDEBAR_WIDTH = 280;
