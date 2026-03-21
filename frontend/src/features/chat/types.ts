// ─── Chat Feature Types ──────────────────────────────────────────────────────

export type MessageRole = "user" | "assistant" | "system";

export interface Source {
  /** Document title or filename */
  title: string;
  /** Relevant content snippet */
  content: string;
  /** Relevance score (0-1) */
  score: number;
  /** Optional metadata (page number, chunk index, etc.) */
  metadata?: Record<string, unknown>;
}

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  metadata?: {
    model?: string;
    latency?: number;
  isStreaming?: boolean;
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

// ─── API Request / Response Shapes ───────────────────────────────────────────

export interface SendMessageRequest {
  message: string;
  chat_id?: string;
  settings?: {
    model?: string;
    temperature?: number;
    rag?: {
      strategy?: string;
      top_k?: number;
      rerank?: boolean;
    };
    memory?: {
      enabled?: boolean;
    };
  };
}

export interface ChatListItem {
  id: string;
  title: string;
  lastMessage?: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
}

// ─── Stream Event Types ──────────────────────────────────────────────────────

export interface StreamTokenEvent {
  token: string;
}

export interface StreamSourcesEvent {
  sources: Source[];
}

export interface StreamDoneEvent {
  done: true;
  message?: string;
  sources?: Source[];
}

export type StreamEvent = StreamTokenEvent | StreamSourcesEvent | StreamDoneEvent;
