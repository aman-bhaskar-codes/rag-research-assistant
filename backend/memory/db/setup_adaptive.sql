-- PHASE 11: ADAPTIVE INTELLIGENCE
-- 🧠 Upgrade memory_entries with ranking and lifecycle signals
ALTER TABLE memory_entries ADD COLUMN IF NOT EXISTS importance_score FLOAT DEFAULT 0.5;
ALTER TABLE memory_entries ADD COLUMN IF NOT EXISTS access_count INT DEFAULT 0;
ALTER TABLE memory_entries ADD COLUMN IF NOT EXISTS last_accessed TIMESTAMP DEFAULT NOW();
ALTER TABLE memory_entries ADD COLUMN IF NOT EXISTS decay_factor FLOAT DEFAULT 1.0;
ALTER TABLE memory_entries ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE;

-- 👤 User Profiles for Personalization
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    preferences JSONB DEFAULT '{}',
    traits JSONB DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 🔗 Memory Relation Graph (Knowledge mapping)
CREATE TABLE IF NOT EXISTS memory_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID REFERENCES memory_entries(id) ON DELETE CASCADE,
    related_memory_id UUID REFERENCES memory_entries(id) ON DELETE CASCADE,
    relation_type TEXT,
    score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ⚡ Production Indexes
CREATE INDEX IF NOT EXISTS idx_memory_user ON memory_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_access ON memory_entries(user_id, last_accessed DESC);
CREATE INDEX IF NOT EXISTS idx_memory_metadata ON memory_entries USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_user_prefs ON user_profiles USING GIN (preferences);
