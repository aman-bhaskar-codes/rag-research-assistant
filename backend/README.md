# 🧠 Backend Orchestration & Control Plane

The backend is not just an API wrapper; it is an **Asynchronous LLM Orchestration Engine**. It acts as the central nervous system, managing concurrency, evaluating user intent, and dynamically piping context through retrieval pipelines.

---

## 📦 Deep Dive: The Backend Tech Stack

### 1. `FastAPI` + `Uvicorn` (The Async Foundation)
Why not Django or Flask? Standard synchronous architectures block the main execution thread while waiting for the LLM to process data. 
*   **FastAPI** is built on top of Starlette and the ASGI async standard.
*   When a user query hits our server, the `Uvicorn` worker handles the connection asynchronously (`async def`). 
*   This means the CPU can pause execution on the LLM network request, go serve 100 other users, and jump back the millisecond the LLM responds. This is how we achieve internet-scale concurrency.

### 2. `Pydantic v2` (The Core Validation Layer)
AI payloads are notoriously messy. We utilize **Pydantic** to enforce strict type-safety across the system boundaries. 
*   Before a query reaches the Orchestrator, Pydantic intercepts the JSON payload, verifies that the `session_id` is a valid UUID, guarantees that the `user_id` matches the correct database format, and throws a safe `422 Unprocessable Entity` error if any data is corrupted.

### 3. Server-Sent Events (SSE) via `StreamingResponse`
Our most complex engineering feat is the real-time interaction layer.
*   We use Python **Generators** (`yield`) to stream data. 
*   As the RAG engine processes the initial context, we `yield` the retrieved documents to the frontend instantly.
*   Then, as the OpenAI/Ollama layer generates text token-by-token, we `yield` those exact string segments directly out of the HTTP connection, creating the famous "typing" effect without ever closing the socket.

---

## ⚙️ The Orchestration Pipeline Explained

When a `POST /query` request arrives, the backend executes the following Pipeline Strategy:

### 1. Intent & Domain Routing
The frontend payload contains a "Domain Mode". The orchestrator inspects this mode and assigns a specific **Retrieval Strategy**.
*   If `mode == "programming"`, the Orchestrator swaps out the Vector database retrieval client for the BM25 lexical keyword client to prioritize exact code matching.

### 2. Context Aggregation
The orchestrator fires off multiple internal tasks simultaneously (`asyncio.gather`):
1.  **Fetch Short-Term Memory**: Pinging the Upstash Redis cache for the last 5 messages in this session.
2.  **Fetch RAG Context**: Passing the user query into the RAG Engine for document retrieval.

### 3. LLM Synthesis Generation
Once the Context and Memory arrays are resolved, the Orchestrator packages them into a massive System Prompt.
We constructed an **Adapter Pattern** for our LLM layer:
*   `OllamaAdapter`: Connects strictly to `localhost:11434` for secure, privacy-first local inference.
*   `GeminiAdapter`: Connects to the Google Cloud REST endpoints via `google-generativeai` for massive reasoning workloads.

The Orchestrator dictates which adapter is spun up based on the user's explicit preference.

---

## 🛡️ Production & Security Considerations

To make this inherently production-ready for Google Cloud Run:
*   **Dependency Injection**: FastAPI `Depends()` is used everywhere. Database connection pools, Redis clients, and RAG Engines are injected at runtime, making unit testing incredibly clean.
*   **Stateless Containers**: The entire orchestration layer is totally stateless. All state lives purely in Neon Postgres or Upstash Redis. If Cloud Run kills our container, the next container spins up and resumes perfectly without losing data.
