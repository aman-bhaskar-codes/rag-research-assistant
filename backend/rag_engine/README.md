# 📄 RAG Engine (Retrieval System)

## 🧠 Overview

The **RAG Engine** is the core knowledge system of this project.
It is responsible for retrieving relevant information from a structured knowledge base and providing high-quality context to the LLM for response generation.

Unlike basic RAG implementations, this system is designed as a **modular, research-grade retrieval engine** supporting multiple strategies, query intelligence, and evaluation.

---

## 🎯 Objectives

* Provide accurate and relevant context for LLM responses
* Support multiple retrieval strategies (vector, keyword, hybrid)
* Improve retrieval quality using query transformation and reranking
* Remain fully independent of API/backend layers
* Enable experimentation and scalability

---

## 🏗️ Architecture

```text
User Query
   ↓
Query Transformation (rewrite, multi-query, HyDE)
   ↓
Multi Retrieval Layer
   ├── Vector Retrieval (pgvector)
   ├── Keyword Retrieval (PostgreSQL FTS)
   └── Hybrid Fusion (RRF)
   ↓
Reranking (LLM-based)
   ↓
Top-N Context Chunks
```

---

## 📦 Core Components

### 1. Document Ingestion Pipeline

Handles transformation of raw data into structured knowledge:

* PDF and text loaders
* Cleaning (remove references, citations, noise)
* Recursive chunking (domain-aware)
* Embedding generation (Ollama / Gemini)
* Storage in PostgreSQL with pgvector

---

### 2. Retrieval Strategies

#### 🔹 Vector Retrieval

* Uses embeddings + pgvector similarity search
* Captures semantic meaning
* Best for conceptual queries

#### 🔹 Keyword Retrieval

* Uses PostgreSQL full-text search (tsvector)
* Captures exact matches and technical terms
* Useful for code, definitions, precise queries

#### 🔹 Hybrid Retrieval

* Combines vector + keyword results
* Uses **Reciprocal Rank Fusion (RRF)**
* Provides best balance of recall and precision

---

### 3. Query Intelligence Layer

Improves retrieval quality before searching:

* **Query Rewriting** → makes queries more specific
* **Multi-Query Generation** → explores multiple perspectives
* **HyDE (Hypothetical Document Embeddings)** → generates synthetic answers for better semantic search

---

### 4. Reranking Layer

Refines retrieved results:

* LLM-based relevance scoring
* Converts Top-K results → Top-N high-quality chunks
* Improves precision significantly

---

### 5. Evaluation System

Ensures retrieval quality is measurable:

* **Recall@K** metric
* Keyword-based ground truth matching
* Evaluation scripts for benchmarking

---

## ⚙️ Retrieval Pipeline

The engine exposes a unified interface:

```python
async def retrieve(query: str, strategy: str = "hybrid", top_k: int = 20, domain: str = "ai_ml"):
```

### Pipeline Flow:

1. Query transformation
2. Retrieval (vector / keyword / hybrid)
3. Rank fusion (if hybrid)
4. Reranking
5. Return structured results

---

## 📤 Output Format

```json
{
  "chunks": [
    {
      "content": "...",
      "score": 0.92,
      "metadata": {
        "chunk_id": "...",
        "document_id": "...",
        "domain": "ai_ml"
      }
    }
  ],
  "meta": {
    "strategy": "hybrid",
    "top_k": 20,
    "top_n": 5
  }
}
```

---

## 🧠 Design Principles

* **Modularity** → each component is swappable
* **Separation of concerns** → no API or DB logic leakage
* **Extensibility** → easy to add new retrievers or rerankers
* **Performance-aware** → batching, limited queries, efficient search
* **Evaluation-driven** → measurable retrieval quality

---

## 🚀 Key Highlights

* Multi-strategy retrieval (vector + keyword + hybrid)
* Query intelligence (rewrite, multi-query, HyDE)
* LLM-based reranking
* Domain-aware design (AI/ML, programming, business)
* Production-ready architecture

---

## 🔮 Future Improvements

* Vectorless retrieval (LLM-only reasoning)
* Feedback-based learning loop
* Advanced rerankers (cross-encoders)
* Adaptive retrieval strategies per query
* Caching and latency optimization

---

## 🧩 Integration

This module is **fully independent** and integrates with the backend via:

```python
retrieval_client → rag_engine.retrieve()
```

It does not depend on:

* FastAPI
* frontend
* orchestration logic
