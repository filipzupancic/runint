-- database/init.sql

CREATE TABLE IF NOT EXISTS benchmark_runs (
    id SERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Context
    model_name VARCHAR(255) NOT NULL,
    engine VARCHAR(50) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    dataset_name VARCHAR(255),
    
    -- Performance
    latency_ms FLOAT,
    throughput_tokens_sec FLOAT,
    error_occurred BOOLEAN DEFAULT FALSE,
    
    -- Flexible Data (The "Pivot" enablers)
    parameters JSONB, 
    metrics JSONB,
    raw_output TEXT
);

-- Optional: Create an index on metrics for future analytics
-- Example: Querying all runs where BLEU score > 20
CREATE INDEX idx_metrics ON benchmark_runs USING gin (metrics);
