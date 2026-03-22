-- PHASE 10: SEMANTIC MEMORY
-- 🧠 Table to store user-specific conversational context as embeddings
CREATE TABLE IF NOT EXISTS memory_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,
    conversation_id UUID,

    content TEXT NOT NULL,

    embedding VECTOR(768), -- Adjusted to Nomic standard (768)

    importance_score FLOAT DEFAULT 0.5,

    metadata JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);

-- ⚡ VECTOR INDEX (High-speed semantic retrieval)
CREATE INDEX IF NOT EXISTS idx_memory_embedding
ON memory_entries
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
