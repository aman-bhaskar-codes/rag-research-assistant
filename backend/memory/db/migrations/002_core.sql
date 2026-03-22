-- 001_extensions.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- USERS
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- CONVERSATIONS (session_id)
CREATE TABLE conversations (
    id UUID PRIMARY KEY,  -- passed from backend (session_id)
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- MESSAGES (CORE MEMORY)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    
    role TEXT CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,

    -- 🔥 IMPORTANT for future
    metadata JSONB,

    -- for ordering
    created_at TIMESTAMP DEFAULT NOW()
);



