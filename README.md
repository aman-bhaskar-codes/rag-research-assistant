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

## 📚 **Modular Architecture Documentation**

The system's advanced complexity is fully documented across its respective microservices. Dive into the engine rooms here:

* 🌐 **[Frontend Architecture](./frontend/README.md)**: Component isolation, Zustand server/client state management, mode-aware interfaces, and SSE streaming mechanisms.
* 🧠 **[Backend Orchestration](./backend/README.md)**: FastAPI gateway, domain routing, pipeline execution, and the interface-driven LLM orchestration layer.
* 🧮 **[RAG Engine Layer](./backend/rag_engine/README.md)**: Vector + BM25 hybrid retrieval pipelines, Query Intelligence (HyDE), and Reciprocal Rank Fusion logic.
* 💾 **[Memory & Database Layer](./backend/memory/README.md)**: Upstash Redis caching strategies, Neon pgvector storage mechanisms, and semantic long-term memory pruning.

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

## ⚙️ **Infrastructure & Deployment (The Engine Room)**

This repository follows a strict **lean production strategy**: 
> *Build like production — run like a startup (minimal cost).*

Our core principles: Use **serverless where possible**, avoid always-on infrastructure, keep services **loosely coupled**, and optimize for **cold start + cost efficiency**.

### 🏗️ Architecture Overview

```text
       Frontend (Next.js)
              ↓
  Cloud Run (FastAPI Backend)
              ↓
-----------------------------------
| Neon (Postgres + pgvector)      |
| Upstash Redis (Serverless Cache)|
| Multi-Model LLM Layer           |
-----------------------------------
```

### 📦 Core Components

**1. Backend Deployment (Cloud Run)**
The FastAPI backend is containerized and deployed using **Google Cloud Run**. It scales to zero, offers a free tier, and autoscales based on traffic.
* *Key Config:* Memory: `512Mi`, CPU: `1`, Min instances: `0`, Max instances: `2`.

**2. Containerization (Docker)**
Located in `infra/docker/backend/`. Features a lightweight image (`python:3.11-slim`), optimized build caching, and a production-ready ASGI server compatible with Cloud Run's dynamic port injection.

**3. Database (Neon Serverless Postgres)**
We use Neon instead of Cloud SQL to eliminate always-on costs. It supports `pgvector` for embeddings, scales automatically, and is ideal for early-stage RAG systems.

**4. Cache Layer (Upstash Redis)**
Serverless, HTTP-based Redis caching that is incredibly Cloud Run friendly. We cache retrieval results, embeddings, and response layers to reduce LLM latency and API costs.

**5. Authentication (Auth0 + Google Login)**
Auth0 handles identity. The infrastructure provides secure secret handling via `infra/env/`, the backend validates strict JWTs, and the frontend manages elegant login/logout flows.

---

## 🚀 **Deployment Workflow**

1. **Build & Tag image for Artifact Registry:**
```bash
docker build -t rag-backend -f infra/docker/backend/Dockerfile .
docker tag rag-backend asia-south1-docker.pkg.dev/PROJECT_ID/rag-backend-repo/rag-backend:latest
docker push asia-south1-docker.pkg.dev/PROJECT_ID/rag-backend-repo/rag-backend:latest
```

2. **Deploy to Cloud Run (Scale-to-Zero):**
```bash
gcloud run deploy rag-backend \
  --image asia-south1-docker.pkg.dev/PROJECT_ID/rag-backend-repo/rag-backend:latest \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 2 \
  --min-instances 0 \
  --port 8080
```

3. **Inject Secrets into Cloud Run:**
```bash
gcloud run services update rag-backend \
  --update-env-vars DATABASE_URL=...,REDIS_URL=...,GEMINI_API_KEY=...
```

---

## 💰 **Cost & Performance Optimization Strategy**

- **Free-Tier Usage:** Cloud Run (scale to zero), Neon (Serverless DB), Upstash (Free Redis tier).
- **Avoided Traps:** Absolutely no Cloud SQL (always billed), no always-on VMs, no GPU workloads.
- **Async-First Design:** Optimized for Cloud Run concurrency with non-blocking DB calls and SSE streaming.
- **Query Optimization:** Top-K reduced (5 → rerank → 3), chunk sizes strictly clamped (300-500 tokens).

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
