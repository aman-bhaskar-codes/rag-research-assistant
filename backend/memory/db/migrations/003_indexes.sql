-- FAST CHAT RETRIEVAL
CREATE INDEX idx_messages_conversation_created
ON messages(conversation_id, created_at DESC);

-- USER CONVERSATIONS
CREATE INDEX idx_conversations_user
ON conversations(user_id);

-- JSON metadata (future filtering)
CREATE INDEX idx_messages_metadata
ON messages USING GIN (metadata);

CREATE INDEX idx_messages_pagination
ON messages(conversation_id, id DESC);

-- document lookup
CREATE INDEX idx_documents_domain
ON documents(domain);

-- chunk lookup
CREATE INDEX idx_chunks_document
ON document_chunks(document_id);

-- 🔥 VECTOR INDEX (CORE OF RAG)
CREATE INDEX idx_chunks_embedding
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);