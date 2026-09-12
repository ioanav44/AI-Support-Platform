-- V002__add_vector_columns.sql
-- Add pgvector support for semantic search

-- Create pgvector extension if not exists
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to tickets
ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS embedding vector(384);

-- Create index for vector similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS idx_tickets_embedding_cosine 
ON tickets USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Add clustering metadata to tickets
ALTER TABLE tickets
ADD COLUMN IF NOT EXISTS cluster_id INTEGER,
ADD COLUMN IF NOT EXISTS outlier_score FLOAT,
ADD COLUMN IF NOT EXISTS is_anomaly BOOLEAN DEFAULT false;

-- Create emerging_issues table
CREATE TABLE IF NOT EXISTS emerging_issues (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(50) DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, CRITICAL
    status VARCHAR(50) DEFAULT 'NEW', -- NEW, MONITORING, RESOLVED, CLOSED
    why_detected TEXT,
    ticket_count INTEGER DEFAULT 0,
    last_occurrence TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Create pivot table: emerging_issue -> tickets (many-to-many)
CREATE TABLE IF NOT EXISTS emerging_issue_tickets (
    emerging_issue_id BIGINT NOT NULL,
    ticket_id BIGINT NOT NULL,
    PRIMARY KEY (emerging_issue_id, ticket_id),
    FOREIGN KEY (emerging_issue_id) REFERENCES emerging_issues(id) ON DELETE CASCADE,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tickets_cluster_id ON tickets(cluster_id);
CREATE INDEX IF NOT EXISTS idx_tickets_is_anomaly ON tickets(is_anomaly);
CREATE INDEX IF NOT EXISTS idx_emerging_issues_status ON emerging_issues(status);
CREATE INDEX IF NOT EXISTS idx_emerging_issues_severity ON emerging_issues(severity);
CREATE INDEX IF NOT EXISTS idx_emerging_issue_tickets_issue ON emerging_issue_tickets(emerging_issue_id);
