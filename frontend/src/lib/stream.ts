import { API_BASE_URL, STREAM_DONE_SIGNAL } from "@/config/constants";
import type { Source } from "@/features/chat/types";

// ─── Stream Callback Types ──────────────────────────────────────────────────

export interface StreamCallbacks {
  /** Called for each text token received */
  onToken: (token: string) => void;
  /** Called when sources are received (may come during or after stream) */
  onSources?: (sources: Source[]) => void;
  /** Called when the stream completes successfully */
  onDone: () => void;
  /** Called on any error */
  onError: (error: Error) => void;
}

export interface StreamRequestBody {
  message: string;
  chat_id?: string;
  settings?: Record<string, unknown>;
}

// ─── SSE Stream Reader ──────────────────────────────────────────────────────

/**
 * Initiates a streaming chat request via Server-Sent Events.
 *
 * Uses `fetch()` with a ReadableStream to process SSE events in real-time.
 * Each event line follows the format: `data: {"token": "..."}`
 * The stream ends with: `data: [DONE]`
 *
 * @returns An AbortController that can be used to cancel the stream
 */
export function streamChat(
  endpoint: string,
  body: StreamRequestBody,
  callbacks: StreamCallbacks
): AbortController {
  const controller = new AbortController();

  const processStream = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Stream request failed: ${response.status}`
        );
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("Response body is not readable");
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          // Process any remaining buffer
          if (buffer.trim()) {
            processSSELine(buffer.trim(), callbacks);
          }
          callbacks.onDone();
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // Process complete lines
        const lines = buffer.split("\n");
        buffer = lines.pop() || ""; // Keep incomplete line in buffer

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed) {
            processSSELine(trimmed, callbacks);
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        // Stream was intentionally cancelled
        callbacks.onDone();
        return;
      }
      callbacks.onError(
        error instanceof Error ? error : new Error("Unknown streaming error")
      );
    }
  };

  processStream();

  return controller;
}

// ─── SSE Line Parser ────────────────────────────────────────────────────────

function processSSELine(line: string, callbacks: StreamCallbacks): void {
  // SSE format: `data: <payload>`
  if (!line.startsWith("data: ")) return;

  const payload = line.slice(6); // Remove "data: " prefix

  // Check for done signal
  if (payload === STREAM_DONE_SIGNAL) {
    return; // onDone will be called when the stream closes
  }

  try {
    const parsed = JSON.parse(payload);

    // Token event
    if (parsed.token !== undefined) {
      callbacks.onToken(parsed.token);
    }

    // Sources event (may come as a separate event or within the final event)
    if (parsed.sources && callbacks.onSources) {
      callbacks.onSources(parsed.sources);
    }
  } catch {
    // Non-JSON data line — treat as raw text token
    callbacks.onToken(payload);
  }
}
