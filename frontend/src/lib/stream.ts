export async function streamChat({
  query,
  metadata,
  onToken,
  onDone,
  onError,
}: {
  query: string;
  metadata?: Record<string, any>;
  onToken: (token: string) => void;
  onDone: (data?: any) => void;
  onError: (err: any) => void;
}) {
  try {
    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, ...metadata }),
    });

    if (!res.body) throw new Error("No response body");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Split by newline (SSE-style or chunked JSON)
      const parts = buffer.split("\n");

      for (let i = 0; i < parts.length - 1; i++) {
        const chunk = parts[i].trim();
        if (!chunk) continue;

        try {
          const parsed = JSON.parse(chunk);

          if (parsed.token) {
            onToken(parsed.token);
          }

          if (parsed.done) {
            onDone(parsed);
          }
        } catch (e) {
          // ignore partial JSON
        }
      }

      buffer = parts[parts.length - 1];
    }

    onDone();
  } catch (err) {
    onError(err);
  }
}
