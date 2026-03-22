# 🌐 Frontend Architecture & Engineering

The frontend is not merely a chat interface. It is an **adaptive intelligence control panel** built on an edge-native stack designed to parse continuous bytecode streams in real-time.

---

## 📦 Deep Dive: The Frontend Tech Stack

We avoided bloated legacy frameworks and built the UI using the absolute bleeding-edge of React engineering:

### 1. `Next.js 14` (App Router)
We utilized Next.js Server Components for initial payload delivery, but strictly offloaded the intensive streaming logic to Client Components. The App router allows us to keep routing clean while bridging environment variables (like API URLs) securely to the client.

### 2. `Zustand` over Redux
Standard state managers like Redux trigger massive re-render cycles that destroy UI performance during high-speed LLM streaming. **Zustand** gives us atomic, isolated store slices. When a message chunk arrives, Zustand cleanly updates the `partialMessage` buffer without causing unrelated components (like the sidebar or settings modal) to re-render.

### 3. Server-Sent Events (SSE) & The `fetch` API
Real-time typing isn't magic; it's streaming byte chunks. We consume the FastAPI backend stream using the native browser `ReadableStream`.
*   **How it works**: The user sends a POST request. The server doesn't close the connection; it holds it open via `text/event-stream`.
*   We use a while-loop (`await reader.read()`) to catch byte chunks as they are emitted from the backend.
*   A custom string decoder parses the JSON payloads instantly and pushes them into the Zustand state.

### 4. `react-markdown` & `rehype-highlight`
LLMs output raw markdown. We pipe the dynamically updating text string through `react-markdown`, which renders formatting on the fly. We paired it with `rehype-highlight` so that when the RAG engine generates Python or JavaScript code blocks, they are automatically wrapped in syntax highlighting.

### 5. `framer-motion` & `tailwind-css`
The visual identity relies on **Tailwind CSS** for rapid glassmorphism and gradient layout utilities. We integrated **Framer Motion** for physics-based layout transitions. When a new message appears, it doesn't snap abruptly into existence; it smoothly animates into the DOM tree.

---

## 🏗️ The Domain "Mode" System (Core Innovation)

The frontend's primary architectural innovation is its **Domain Mode Engine**. 

Instead of hiding the RAG complexity, we expose it. When a user clicks "AI Research" or "Programming", the frontend injects a specific intent payload into the API request. 

**This enables the frontend to act as the steering wheel for the backend:**
1.  **AI/ML Mode**: Triggers the backend to use HyDE and Vector Search for deep academic synthesis.
2.  **Programming Mode**: Tells the backend to switch entirely to BM25 exact-keyword matching to find variable names and syntax rules.

This fundamentally transforms the app from a generic chatbot into a **highly specialized research application**.

---

## 🐞 The RAG Debug & Transparency UI

A critical requirement for enterprise AI is transparency. We built a visual **Debug Panel** component. 

When a user enables "Debug Mode", the UI intercepts specialized metrics payloads attached to the SSE stream. It explicitly displays:
*   The raw document chunks that were successfully retrieved by the backend.
*   The mathematical similarity scores of those chunks.
*   The microsecond latencies of the Vector Database.

This layer proves the intelligence of the system visually to the user.

---

## ⚡ Error Boundary & Crash Protection

During e2e testing, we encountered the Next.js "Red Screen of Death" when the FastAPI backend rejected malformed payloads. 

We engineered a **graceful error boundary** inside our `stream.ts` utility. If FastAPI throws a `422 Unprocessable Entity` or `500 Internal Error`, the React application catches the raw HTTP status, terminates the stream locally, and gracefully types out the explicit backend error directly into the user's Chat Bubble. The application never crashes.
