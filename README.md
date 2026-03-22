<div align="center">

<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Robot.png" alt="Robot" width="80" height="80" />

# **RAG Research Assistant**
*Enterprise-Grade LLM Engineering & Autonomous Intelligence Lab*

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/Neon_Serverless_DB-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech/)
[![Upstash](https://img.shields.io/badge/Upstash_Redis-FF0000?style=for-the-badge&logo=redis&logoColor=white)](https://upstash.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=24&pause=1000&color=3B82F6&center=true&vCenter=true&width=800&height=60&lines=Multi-Agent+Generative+AI;Hybrid+Vector+%2B+BM25+Retrieval;Streaming+Server-Sent+Events+(SSE);Ollama+(Local)+%2B+Gemini+(Cloud)" alt="Typing SVG" />

</div>

---

## 🎬 **Cinematic Overview**

Welcome to the **RAG Research Assistant** — an elite, production-grade intelligence layer designed to mimic the architecture of enterprise ChatGPT-level systems. This is not a simple wrapper. It is a deeply engineered, multi-modal autonomous research lab built across a highly decoupled serverless microservices architecture.

We have engineered a system that doesn't just read documents; it dynamically routes your query, mathematically fuses keyword and vector retrieval algorithms, and synthesizes answers via local (Ollama) or cloud (Gemini) intelligence layers.

> **Design Philosophy**: *Zero idle cost. Scale to zero. High precision.*

---

## 🧠 **System Architecture (The Deep Dive)**

<div align="center">

> *(Insert High-Resolution Architecture Diagrams Here)*
> 
> *The blueprint maps our data flow from the NextJS Edge -> FastAPI WebSockets -> Hybrid RAG Lab -> Memory Lake -> LLM Layer.*

</div>

The system is compartmentalized into **Four Core Pillars**:

### 1. **Frontend (The Edge UI)**
Built in **Next.js 14 (Turbopack)** and **Tailwind CSS**. It replicates an elite ChatGPT-style streaming interface. It manages state via Zustand and communicates with the backend exclusively through low-latency **Server-Sent Events (SSE)**, ensuring real-time token streaming and dynamic metadata injection (telemetry, latencies, chunk citations).

### 2. **API Gateway & Orchestrator (The Brain)**
Powered by **FastAPI** running on Uvicorn async workers.
- **Session Manager**: Manages volatile and persistent conversational boundaries.
- **Domain Router**: A lightweight classification layer that dynamically routes standard prompts into specialized logic lanes based on the user's intent.

### 3. **The RAG Engine (The Lab)**
The core intelligence retrieval mechanism is completely decoupled and implements state-of-the-art information retrieval:
*   **Vector Retrieval (pgvector)**: Captures semantic and contextual meaning.
*   **Keyword Search (BM25)**: Ensures exact-match precision for technical jargon, acronyms, and proper nouns.
*   **Vectorless Entity Graph**: Maps relationships without relying on dense vectors.
*   **Reciprocal Rank Fusion (RRF) & Cross-Encoder Reranker**: The results from pgvector and BM25 are mathematically fused and then reranked by a cross-encoder model to guarantee only the highest-fidelity context is injected into the prompt window.

### 4. **Memory System & LLM Layer**
- **Neon Postgres (Serverless)**: Houses `Users/Chats`, raw `Documents`, and chunked embeddings via `pgvector`.
- **Upstash Redis (Serverless)**: Accelerates history retrieval and caches heavily queried semantic networks.
- **Multi-Model LLM Layer**: Completely abstract adapter pattern supporting **Ollama** (for local, privacy-first execution) and **Gemini 1.5 Pro** (for advanced cloud-scale reasoning).

---

## 🧪 **Domain Modes**

The Assistant dynamically shifts its system prompt, retrieval strategy, and chunking mechanism based on the selected domain:

| Domain | Retrieval Strategy | Highlight Focus |
| :--- | :--- | :--- |
| 🔬 **AI / ML Research** | Deep Synthesis / HyDE | Academic citations, paper analysis, methodology breakdowns. |
| 💻 **Programming / Docs** | Exact BM25 / Code-Block Chunker | Syntax accuracy, stack traces, precise documentation search. |
| 📈 **Business / Startup** | Hybrid Trend Mapping | Market intelligence, competitor tracking, trend synthesis. |

---

## 🏗️ **How We Built This (Step-by-Step Evolution)**

Creating an elite platform from scratch required rigorous engineering discipline. Here is how we evolved the codebase:

### **Phase 1: The Asynchronous Core ⚡**
We started by establishing the lowest-level communication protocol. Standard HTTP requests were too slow for LLM generation. We built a custom **SSE (Server-Sent Events)** pipeline in `FastAPI` and `Next.js`, intercepting raw byte chunks (`data: {...}`) and parsing them into a beautiful, jitter-free typing animation on the React frontend.

### **Phase 2: Hybrid Memory & The Vector Lab 🧮**
Basic RAG (Vector-only) suffers from low recall on precise keywords. We completely overhauled the retrieval pipeline. We deployed **Neon Serverless Postgres** with the `pgvector` extension. Then, we wrote a pipeline that fires off async queries to both pgvector AND a BM25 index, mathematically fusing them using Reciprocal Rank Fusion, before passing them to the Synthesis generator.

### **Phase 3: The Identity & Telemetry Layer 🛡️**
To transition from a "demo" to an "application", we implemented strict `schema` validation using Pydantic. By enforcing UUID payloads for `user_id` and `session_id`, we structured our data lakes to eventually support robust Auth0 multi-tenant isolation. Telemetry was injected into the SSE stream to pass back microsecond-accurate retrieval latencies to the frontend developer console.

### **Phase 4: Serverless Caching 🚀**
To prevent expensive repeated LLM hits and Database lookups, we integrated **Upstash Redis**. By keeping it HTTP-based, we ensured it remained fully compatible with Cloud Run and Vercel Edge functions, operating with zero idle cost.

### **Phase 5: Dockerization & Cloud Native Scale-to-Zero 🐳**
Finally, we hardened the backend. We crafted a multi-stage `Dockerfile` running as a non-root `appuser`. The `settings` configuration was bound strictly to environment variables, allowing the completely stateless container to be pushed to **Google Artifact Registry** and deployed to **Google Cloud Run** — securely capable of scaling from zero up to hundreds of concurrent requests dynamically.

---

## 💻 **Local Development & Deployment Guide**

### 1. Environment Setup
Clone the repository and copy the example environment files.
```bash
cp backend/infra/env/backend.env.example backend/.env
cp frontend/infra/env/frontend.env.example frontend/.env.local
```

You will need to provide your own:
- **Neon Postgres Connection URL:** `postgresql+asyncpg://...`
- **Upstash Redis URL & Token**
- **Gemini API Key** (Or run Ollama locally on `11434`)

### 2. Database Initialization
Run the raw SQL architecture scripts against your Neon Database to establish the Knowledge Graph tables:
```bash
psql $DATABASE_URL -f backend/memory/db/setup.sql
psql $DATABASE_URL -f backend/memory/db/setup_adaptive.sql
psql $DATABASE_URL -f backend/memory/db/setup_semantic.sql
```

### 3. Spin Up The Infrastructure
Everything is containerized for exact parity with Google Cloud Run.
```bash
# Start the Backend (Port 8080)
docker build -t rag-backend -f infra/docker/backend/Dockerfile .
docker run -d -p 8080:8080 --env-file .env rag-backend

# Start the Frontend (Port 3000)
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to interact with your elite intelligence system.

---

## 🔮 **Future Roadmap**

*   [ ] **Agentic Patching Workflow:** Integrate autonomous sub-agents capable of executing verified Python scripts based on queries.
*   [ ] **Full Neo4j Knowledge Graph Integration:** Transition from simulated relational entities to a massive NoSQL graph backend.
*   [ ] **Enterprise Auth0 Integration:** Enforce strict RBAC (Role Based Access Control) natively across Next.js Middleware and FastAPI Dependencies.
*   [ ] **Terraform Infrastructure as Code (IaC):** One-click rollout of GCP Cloud Run, Artifact Registry, and Secrets Manager.

<br>

<div align="center">
  <sub>Built with precision globally by the <b>LLM Engineering Lab Engine</b>.</sub><br>
  <sub><i>"Advanced architecture requires advanced discipline."</i></sub>
</div>
