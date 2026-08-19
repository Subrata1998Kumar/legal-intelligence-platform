-- Enable the pgvector extension for high-dimensional vector search
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Users table for Authentication and Role-Based Access Control (RBAC)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Bcrypt hash of password
    role VARCHAR(50) NOT NULL CHECK (role IN ('Legal_Officer', 'Senior_Advisor', 'Admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Documents Metadata Table for Access Authorization and Provenance
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL, -- SHA-256 for deduplication and integrity auditing
    security_clearance VARCHAR(50) NOT NULL DEFAULT 'Legal_Officer' CHECK (security_clearance IN ('Legal_Officer', 'Senior_Advisor', 'Admin')),
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Document Chunks Table with vector embeddings (paraphrase-multilingual:278m - 768 dimensional dense vector)
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL, -- Raw text content of the chunk
    embedding VECTOR(768), -- Vector representation of semantic content
    is_table BOOLEAN DEFAULT FALSE,
    table_json JSONB, -- Stores structured tables as JSON if parsed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Session History and Chat Memory tables for PostgreSQL-based persistence
CREATE TABLE IF NOT EXISTS chat_sessions (
    id VARCHAR(100) PRIMARY KEY, -- Session ID UUID or unique hash
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Creating high-performance HNSW index on the vector embeddings
-- HNSW builds a multi-layer proximity graph to perform fast Approximate Nearest Neighbor (ANN) search.
-- We use L2 distance (vector_l2_ops) or cosine distance (vector_cosine_ops) based on our retriever needs.
CREATE INDEX IF NOT EXISTS document_chunks_hnsw_idx 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
