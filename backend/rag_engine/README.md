# 🧮 RAG Engine (Retrieval-Augmented Generation)

The RAG Engine is the true intelligence layer of the system. Native LLMs hallucinate; the RAG module mathematically guarantees factual accuracy by pulling context from structured knowledge vectors prior to generation.

---

## 📦 Deep Dive: The RAG Tech Stack

To build a research-grade RAG pipeline, we combined several highly specialized Python algorithms.

### 1. `sentence-transformers` & `FastEmbed`
We parse PDFs and text documents and chunk them algorithmically (usually 300 to 500 tokens). We then use local embedding models to convert those English text chunks into high-dimensional numerical vectors (lists of 1536 float numbers). 

### 2. BM25 (Best Matching 25) Keyword Algorithms
Vectors are great for *semantic meaning* (e.g., matching "puppy" to "dog"), but terrible for exact keyword overlap (matching a specific API variable like `getUserProfile()`). We implemented a pure **BM25 TF-IDF** algorithm, heavily backed by PostgreSQL's native full-text search (`tsvector`), to calculate term frequency.

### 3. Reciprocal Rank Fusion (RRF)
When the user asks a question, we actually do two separate searches simultaneously: an Index Vector Search and a BM25 Keyword Search. 
*   **The Problem:** Vector DBs return a cosine similarity score (0.0 to 1.0), and BM25 returns an arbitrarily massive integer score (like 42.5). You cannot compare them.
*   **The Solution:** We run an **RRF algorithm**, which ignores the raw scores and entirely relies on the *Rank Position* of the chunk to fuse both lists mathematically into a single, high-fidelity ranking list.

### 4. Cross-Encoder Reranking
We then take the top 20 chunks from the RRF output, and run them through a much heavier Cross-Encoder LLM. The Cross-Encoder reads the original question and the chunk *simultaneously* and assigns a much more accurate relevance score, cutting the top 20 chunks down to the top 3 most pristine pieces of context.

---

## 🧠 Query Transform Intelligence Operations

Before we even search the database, the Engine manipulates the user's prompt to increase retrieval surface area:

### 1. Hypothetical Document Embeddings (HyDE)
If a user asks: *"What is zero-shot learning?"*
The engine first asks the LLM to blindly guess the answer: *"Zero-shot learning is a machine learning paradigm where..."*
We then take that *fake, generated answer*, embed it into a vector, and search the Vector Database using the fake answer instead of the question. This astronomically increases similarity matching precision.

### 2. Query Expansion (Multi-Query)
If the user asks: *"How to deploy Next.js with FastAPI?"*
The engine uses an LLM to split this into 3 hidden queries:
1. *"FastAPI server deployment mechanisms"*
2. *"Next.js production build architectures"*
3. *"Dockerizing Next.js and FastAPI together"*
We run 3 parallel searches, vastly expanding the recall of our database hit.

---

## 🧩 Architectural Decoupling

The RAG Engine was built strictly decoupled from the FastAPI API routes. 
We wrote an internal `RetrievalClient` that can be imported completely autonomously anywhere in the backend logic.

```python
results = await rag_engine.retrieve(
    query="Explain NextJS streaming", 
    strategy="hybrid", 
    top_k=5
)
```

This strict architectural separation means if an AI Agent needs to independently search the database during a deep thought loop, it can access the exact same RAG pipeline without ever touching an HTTP request layer.
