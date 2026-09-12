ALTER TABLE tickets ADD COLUMN IF NOT EXISTS embedding vector(384);
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS cluster_id INTEGER;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS outlier_score DOUBLE PRECISION;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS is_anomaly BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_tickets_embedding ON tickets USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_tickets_cluster_id ON tickets(cluster_id);
CREATE INDEX IF NOT EXISTS idx_tickets_is_anomaly ON tickets(is_anomaly);
