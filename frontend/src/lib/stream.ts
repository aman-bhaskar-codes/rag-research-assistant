import { API_BASE_URL } from "@/config/constants";

export interface StreamCallbacks {
  onToken: (token: string) => void;
  onMeta?: (meta: any) => void;
  onDone: () => void;
  onError: (err: any) => void;
}

export async function streamChat(
  payload: any,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
) {
  const { onToken, onMeta, onDone, onError } = callbacks;

  try {
    const res = await fetch(`${API_BASE_URL}/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal,
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      let errorMessage = errorData.error?.message || `HTTP error! status: ${res.status}`;
      
      // Handle FastAPI standard validation errors (422)
      if (errorData.detail && Array.isArray(errorData.detail)) {
        errorMessage = `Validation Error: ${errorData.detail.map((e: any) => `${e.loc.join('.')}: ${e.msg}`).join(', ')}`;
      }
      
      throw new Error(errorMessage);
    }

    if (!res.body) throw new Error("No response body");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // SSE chunks are separated by double newlines
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        
        const data = line.replace("data: ", "").trim();
        if (!data) continue;

        try {
          // Standard SSE: parse as JSON
          const parsed = JSON.parse(data);
          
          if (typeof parsed === "string") {
            onToken(parsed);
          } else if (parsed && typeof parsed === "object") {
            if (parsed.type === "metadata") {
              onMeta?.(parsed);
            } else {
              // Fallback for other JSON types or raw tokens that happen to be JSON
              onMeta?.(parsed);
            }
          }
        } catch (e) {
          // If not JSON, it's a raw token string from the LLM
          onToken(data);
        }
      }
    }

    onDone();
  } catch (err: any) {
    if (err.name === 'AbortError') return;
    onError(err);
  }
}
