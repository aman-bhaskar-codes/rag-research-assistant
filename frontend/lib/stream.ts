import { Source } from "./store";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface StreamCallbacks {
  onSources: (sources: Source[]) => void;
  onToken: (token: string) => void;
  onRelated: (questions: string[]) => void;
  onDone: (meta: Record<string, unknown>) => void;
  onError: (msg: string) => void;
}

function safeParse(payload: string): unknown {
  try { return JSON.parse(payload); }
  catch { return payload; }
}

export async function streamSearch(
  params: {
    query: string;
    sessionId: string;
    focusMode: string;
    model: string;
    useWeb: boolean;
    useRag: boolean;
  },
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${API_URL}/search/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: params.query,
      session_id: params.sessionId,
      focus_mode: params.focusMode,
      model: params.model,
      use_web: params.useWeb,
      use_rag: params.useRag,
    }),
    signal,
  });

  if (!res.ok) {
    const text = await res.text();
    callbacks.onError(`API error ${res.status}: ${text}`);
    return;
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let currentEvent = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        const payload = line.slice(6);
        try {
          switch (currentEvent) {
            case "sources":
              callbacks.onSources(JSON.parse(payload));
              break;
            case "token":
              // Token payload is a raw string OR JSON-encoded string
              // Backend sends json.dumps(token) which produces "quoted string"
              // But if it's a raw string, safeParse returns it as-is
              const parsed = safeParse(payload);
              callbacks.onToken(typeof parsed === "string" ? parsed : String(parsed));
              break;
            case "related":
              callbacks.onRelated(JSON.parse(payload));
              break;
            case "done":
              callbacks.onDone(JSON.parse(payload));
              break;
            case "error":
              const errMsg = safeParse(payload);
              callbacks.onError(typeof errMsg === "string" ? errMsg : String(errMsg));
              break;
          }
        } catch {
          // For token events, pass the raw payload directly
          if (currentEvent === "token") {
            callbacks.onToken(payload);
          }
        }
        currentEvent = "";
      }
    }
  }
}
