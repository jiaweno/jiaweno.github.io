-- Conceptual Database Schema for AI Learning Management System
-- Target RDBMS: PostgreSQL

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User Roles (Example, can be expanded)
-- CREATE TYPE user_role AS ENUM ('student', 'instructor', 'admin');

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    -- role user_role DEFAULT 'student', -- Example for roles
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Document Status Enum Type
CREATE TYPE document_status AS ENUM ('pending', 'processing', 'completed', 'failed');

-- Documents Table
-- Stores metadata about uploaded learning materials
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    s3_url VARCHAR(1024) NOT NULL, -- URL to the document in S3
    status document_status DEFAULT 'pending',
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- extracted_text_s3_url VARCHAR(1024), -- Optional: if extracted text is too large and stored separately
    -- vector_id VARCHAR(255), -- Optional: ID from vector database if needed here
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge Points Table
-- Stores individual concepts or sections extracted from documents
CREATE TABLE IF NOT EXISTS knowledge_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    content_summary TEXT, -- Summary of the knowledge point
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    -- parent_kp_id UUID REFERENCES knowledge_points(id) ON DELETE SET NULL, -- For dependency graph
    -- vector_embedding_s3_url VARCHAR(1024), -- If embeddings are stored in S3, or keep in vector DB
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Learning Paths Table
-- Stores curated or generated sequences of knowledge points for users
CREATE TABLE IF NOT EXISTS learning_paths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Learning Path Knowledge Points Association Table (Many-to-Many)
-- Defines the sequence of knowledge points within a learning path
CREATE TABLE IF NOT EXISTS learning_path_knowledge_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Or use composite PK (learning_path_id, knowledge_point_id)
    learning_path_id UUID NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
    knowledge_point_id UUID NOT NULL REFERENCES knowledge_points(id) ON DELETE CASCADE,
    sequence_order INTEGER NOT NULL, -- To maintain order within the path
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (learning_path_id, knowledge_point_id),
    UNIQUE (learning_path_id, sequence_order)
);

-- Quiz Attempts Table
-- Stores records of user attempts on quizzes/tests
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    learning_path_id UUID REFERENCES learning_paths(id) ON DELETE SET NULL, -- Optional: if quiz is path-specific
    knowledge_point_id UUID REFERENCES knowledge_points(id) ON DELETE SET NULL, -- Optional: if quiz is KP-specific
    score FLOAT, -- Overall score for the attempt
    questions_answers JSONB, -- Store questions, user's answers, correct answers, individual scores
    feedback TEXT, -- GPT generated feedback or manual feedback
    attempted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Optional: User Progress / Mastery Table
-- Could be used to store mastery level per knowledge point for each user
CREATE TABLE IF NOT EXISTS user_knowledge_point_mastery (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    knowledge_point_id UUID NOT NULL REFERENCES knowledge_points(id) ON DELETE CASCADE,
    mastery_level FLOAT DEFAULT 0.0, -- e.g., 0.0 to 1.0
    last_assessed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, knowledge_point_id)
);


-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_documents_owner_id ON documents(owner_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_points_document_id ON knowledge_points(document_id);
CREATE INDEX IF NOT EXISTS idx_learning_paths_user_id ON learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_lp_kp_learning_path_id ON learning_path_knowledge_points(learning_path_id);
CREATE INDEX IF NOT EXISTS idx_lp_kp_knowledge_point_id ON learning_path_knowledge_points(knowledge_point_id);
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user_id ON quiz_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_kp_mastery_user_id ON user_knowledge_point_mastery(user_id);
CREATE INDEX IF NOT EXISTS idx_user_kp_mastery_kp_id ON user_knowledge_point_mastery(knowledge_point_id);

-- Trigger function to update 'updated_at' timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the trigger to tables
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_points_updated_at
BEFORE UPDATE ON knowledge_points
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_paths_updated_at
BEFORE UPDATE ON learning_paths
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Add more triggers for other tables as needed (e.g., quiz_attempts, user_knowledge_point_mastery)
CREATE TRIGGER update_quiz_attempts_updated_at
BEFORE UPDATE ON quiz_attempts
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_kp_mastery_updated_at
BEFORE UPDATE ON user_knowledge_point_mastery
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

COMMENT ON COLUMN documents.s3_url IS 'URL to the raw document file in AWS S3';
COMMENT ON COLUMN documents.status IS 'Processing status of the document';
COMMENT ON COLUMN knowledge_points.content_summary IS 'AI-generated or manually created summary of the content';
COMMENT ON TABLE learning_path_knowledge_points IS 'Associates knowledge points to learning paths and defines their order';
COMMENT ON COLUMN quiz_attempts.questions_answers IS 'JSONB field to store array of questions, user answers, correct answers, options, and scores per question';
COMMENT ON TABLE user_knowledge_point_mastery IS 'Tracks user-specific mastery level for each knowledge point';
