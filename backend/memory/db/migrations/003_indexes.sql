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