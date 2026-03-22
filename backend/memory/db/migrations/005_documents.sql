-- DOCUMENTS (high-level info)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    source TEXT,
    domain TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- DOCUMENT CHUNKS (RAG core)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,

    content TEXT NOT NULL,

    -- 🔥 IMPORTANT: embedding dimension
    embedding VECTOR(1536),

    chunk_index INT,

    metadata JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);