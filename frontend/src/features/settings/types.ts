// ─── Settings Feature Types ──────────────────────────────────────────────────

export type RAGStrategy = "hybrid" | "semantic" | "keyword";

export type Plan = "free" | "premium";

export interface RAGConfig {
  strategy: RAGStrategy;
  top_k: number;
  rerank: boolean;
}

export interface MemoryConfig {
  enabled: boolean;
}

export interface Settings {
  model: string;
  temperature: number;
  rag: RAGConfig;
  memory: MemoryConfig;
  plan: Plan;
}
