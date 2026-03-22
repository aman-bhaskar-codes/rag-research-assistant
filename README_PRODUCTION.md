# 🧠 Adaptive Intelligence RAG Assistant

A production-grade, learning-aware Research Assistant built on a hybrid RAG architecture.

## 🚀 Intelligent Architecture

### 1. Hybrid Retrieval (RAG Engine)
- **Vector Search**: Semantic similarity using Ollama/Gemini embeddings and `pgvector`.
- **Keyword Search**: BM25-based keyword matches for technical precision.
- **RRF Fusion**: Reciprocal Rank Fusion combines both signals for top-tier relevance.
- **Query Intelligence**: Automatic query rewriting, multi-query expansion, and HyDE.

### 2. Adaptive Memory System
- **Long-Term Semantic Recall**: Stores previous user interactions with multi-factor ranking.
- **Adaptive Ranking**: Prioritizes memories based on `Similarity + Importance + Usage + Recency`.
- **Personalization Trait Tracking**: Automatically learns and applies user behavioral traits (e.g., expertise levels, tool preferences).
- **Knowledge Graphing**: Links related memories to provide deeper contextual insight.

### 3. Production Lifecycle
- **Memory Pruning**: Autonomous script (`prune_memory.py`) arches low-value interactions.
- **Evaluation Loop**: Measure retrieval quality with `Recall@k` using local evaluation datasets.

## 🛠️ Tech Stack
- **Backend**: Python 3.13, FastAPI, asyncpg
- **Database**: PostgreSQL + pgvector (Semantic Storage)
- **Cache**: Redis (Short-term Context)
- **AI Models**: Ollama (Local), Google Gemini (Cloud), Rerank (Cross-Encoder)
- **Frontend**: Next.js (Modern Research UI)

## 🏃 Getting Started
1. **Migrations**: `psql -d rag_assistant -f backend/memory/db/setup_semantic.sql`
2. **Setup Adaptive**: `psql -d rag_assistant -f backend/memory/db/setup_adaptive.sql`
3. **Run Dev**: `npm run dev` (Frontend) & `uvicorn main:app` (Backend)

---
*Created with the High-End Agentic Intelligence Loop.*
