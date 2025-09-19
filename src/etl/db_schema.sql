-- ETL Pipeline Database Schema for Novel Content Processing
-- Supporting tables for processed content, entities, and pipeline metadata

-- 1. Processed Content Tables
CREATE TABLE IF NOT EXISTS processed_worldview (
    id SERIAL PRIMARY KEY,
    original_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL DEFAULT 'worldview',
    original_content TEXT,
    cleaned_content TEXT NOT NULL,
    entities_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pipeline_version VARCHAR(50) DEFAULT '1.0',
    content_hash VARCHAR(64),
    validation_score FLOAT DEFAULT 0.0,
    UNIQUE(original_id, content_type)
);

CREATE TABLE IF NOT EXISTS processed_character (
    id SERIAL PRIMARY KEY,
    original_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL DEFAULT 'character',
    original_content TEXT,
    cleaned_content TEXT NOT NULL,
    entities_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pipeline_version VARCHAR(50) DEFAULT '1.0',
    content_hash VARCHAR(64),
    validation_score FLOAT DEFAULT 0.0,
    UNIQUE(original_id, content_type)
);

CREATE TABLE IF NOT EXISTS processed_plot (
    id SERIAL PRIMARY KEY,
    original_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL DEFAULT 'plot',
    original_content TEXT,
    cleaned_content TEXT NOT NULL,
    entities_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pipeline_version VARCHAR(50) DEFAULT '1.0',
    content_hash VARCHAR(64),
    validation_score FLOAT DEFAULT 0.0,
    UNIQUE(original_id, content_type)
);

CREATE TABLE IF NOT EXISTS processed_scene (
    id SERIAL PRIMARY KEY,
    original_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL DEFAULT 'scene',
    original_content TEXT,
    cleaned_content TEXT NOT NULL,
    entities_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pipeline_version VARCHAR(50) DEFAULT '1.0',
    content_hash VARCHAR(64),
    validation_score FLOAT DEFAULT 0.0,
    UNIQUE(original_id, content_type)
);

CREATE TABLE IF NOT EXISTS processed_dialogue (
    id SERIAL PRIMARY KEY,
    original_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL DEFAULT 'dialogue',
    original_content TEXT,
    cleaned_content TEXT NOT NULL,
    entities_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pipeline_version VARCHAR(50) DEFAULT '1.0',
    content_hash VARCHAR(64),
    validation_score FLOAT DEFAULT 0.0,
    UNIQUE(original_id, content_type)
);

-- 2. Entity Recognition Tables
CREATE TABLE IF NOT EXISTS extracted_entities (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(255) NOT NULL UNIQUE,
    canonical_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    mention_count INTEGER DEFAULT 1,
    first_mention_pos INTEGER DEFAULT 0,
    aliases JSONB DEFAULT '[]',
    attributes JSONB DEFAULT '{}',
    relationships JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS entity_mentions (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(255) REFERENCES extracted_entities(entity_id) ON DELETE CASCADE,
    content_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    mention_text VARCHAR(500) NOT NULL,
    normalized_form VARCHAR(255) NOT NULL,
    start_pos INTEGER NOT NULL,
    end_pos INTEGER NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    context TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Data Quality and Validation Tables
CREATE TABLE IF NOT EXISTS validation_results (
    id SERIAL PRIMARY KEY,
    record_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    is_valid BOOLEAN NOT NULL,
    overall_score FLOAT NOT NULL,
    validation_time FLOAT NOT NULL,
    issues_count INTEGER DEFAULT 0,
    critical_issues INTEGER DEFAULT 0,
    error_issues INTEGER DEFAULT 0,
    warning_issues INTEGER DEFAULT 0,
    info_issues INTEGER DEFAULT 0,
    validated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS validation_issues (
    id SERIAL PRIMARY KEY,
    validation_id INTEGER REFERENCES validation_results(id) ON DELETE CASCADE,
    issue_id VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    field_name VARCHAR(255),
    field_value TEXT,
    rule_name VARCHAR(255),
    suggested_fix TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Pipeline Processing Tables
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) NOT NULL UNIQUE,
    content_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    processed_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,
    extracted_entities INTEGER DEFAULT 0,
    validation_errors INTEGER DEFAULT 0,
    processing_rate FLOAT DEFAULT 0.0,
    config JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS pipeline_checkpoints (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(50) NOT NULL,
    last_processed INTEGER DEFAULT 0,
    checkpoint_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(content_type)
);

-- 5. Change Tracking and Versioning Tables
CREATE TABLE IF NOT EXISTS change_log (
    id SERIAL PRIMARY KEY,
    change_id VARCHAR(255) NOT NULL UNIQUE,
    change_type VARCHAR(20) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS data_versions (
    id SERIAL PRIMARY KEY,
    version_id VARCHAR(255) NOT NULL UNIQUE,
    record_id VARCHAR(255) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    author VARCHAR(255) NOT NULL,
    parent_version VARCHAR(255),
    changes JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS conflict_records (
    id SERIAL PRIMARY KEY,
    conflict_id VARCHAR(255) NOT NULL UNIQUE,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    field_name VARCHAR(255) NOT NULL,
    local_value JSONB,
    remote_value JSONB,
    local_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    remote_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    resolution_strategy VARCHAR(50) NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_value JSONB,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- 6. Stream Processing Tables
CREATE TABLE IF NOT EXISTS stream_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL UNIQUE,
    event_type VARCHAR(50) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data JSONB NOT NULL,
    source VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    processed BOOLEAN DEFAULT FALSE,
    retry_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS stream_windows (
    id SERIAL PRIMARY KEY,
    window_id VARCHAR(255) NOT NULL UNIQUE,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    event_count INTEGER DEFAULT 0,
    is_closed BOOLEAN DEFAULT FALSE,
    processed BOOLEAN DEFAULT FALSE,
    metrics JSONB DEFAULT '{}'
);

-- 7. Performance Monitoring Tables
CREATE TABLE IF NOT EXISTS processing_metrics (
    id SERIAL PRIMARY KEY,
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    tags JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_processed_content_original_id ON processed_worldview(original_id);
CREATE INDEX IF NOT EXISTS idx_processed_content_type ON processed_worldview(content_type);
CREATE INDEX IF NOT EXISTS idx_processed_content_hash ON processed_worldview(content_hash);

CREATE INDEX IF NOT EXISTS idx_processed_char_original_id ON processed_character(original_id);
CREATE INDEX IF NOT EXISTS idx_processed_plot_original_id ON processed_plot(original_id);
CREATE INDEX IF NOT EXISTS idx_processed_scene_original_id ON processed_scene(original_id);
CREATE INDEX IF NOT EXISTS idx_processed_dialogue_original_id ON processed_dialogue(original_id);

CREATE INDEX IF NOT EXISTS idx_entities_canonical_name ON extracted_entities(canonical_name);
CREATE INDEX IF NOT EXISTS idx_entities_type ON extracted_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_confidence ON extracted_entities(confidence);

CREATE INDEX IF NOT EXISTS idx_mentions_entity_id ON entity_mentions(entity_id);
CREATE INDEX IF NOT EXISTS idx_mentions_content_id ON entity_mentions(content_id);
CREATE INDEX IF NOT EXISTS idx_mentions_content_type ON entity_mentions(content_type);

CREATE INDEX IF NOT EXISTS idx_validation_record_id ON validation_results(record_id);
CREATE INDEX IF NOT EXISTS idx_validation_content_type ON validation_results(content_type);
CREATE INDEX IF NOT EXISTS idx_validation_valid ON validation_results(is_valid);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_content_type ON pipeline_runs(content_type);

CREATE INDEX IF NOT EXISTS idx_change_log_record_id ON change_log(record_id);
CREATE INDEX IF NOT EXISTS idx_change_log_timestamp ON change_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_change_log_change_type ON change_log(change_type);

CREATE INDEX IF NOT EXISTS idx_versions_record_id ON data_versions(record_id);
CREATE INDEX IF NOT EXISTS idx_versions_timestamp ON data_versions(timestamp);

CREATE INDEX IF NOT EXISTS idx_conflicts_resolved ON conflict_records(resolved);
CREATE INDEX IF NOT EXISTS idx_conflicts_table_record ON conflict_records(table_name, record_id);

CREATE INDEX IF NOT EXISTS idx_stream_events_processed ON stream_events(processed);
CREATE INDEX IF NOT EXISTS idx_stream_events_timestamp ON stream_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_stream_events_type ON stream_events(event_type);

CREATE INDEX IF NOT EXISTS idx_metrics_type_name ON processing_metrics(metric_type, metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON processing_metrics(timestamp);

-- Views for Analytics
CREATE OR REPLACE VIEW entity_statistics AS
SELECT
    entity_type,
    COUNT(*) as total_entities,
    AVG(confidence) as avg_confidence,
    AVG(mention_count) as avg_mentions,
    MAX(updated_at) as last_updated
FROM extracted_entities
GROUP BY entity_type;

CREATE OR REPLACE VIEW processing_summary AS
SELECT
    content_type,
    COUNT(*) as total_processed,
    AVG(validation_score) as avg_validation_score,
    AVG(entities_count) as avg_entities,
    MAX(processed_at) as last_processed
FROM (
    SELECT content_type, validation_score, entities_count, processed_at FROM processed_worldview
    UNION ALL
    SELECT content_type, validation_score, entities_count, processed_at FROM processed_character
    UNION ALL
    SELECT content_type, validation_score, entities_count, processed_at FROM processed_plot
    UNION ALL
    SELECT content_type, validation_score, entities_count, processed_at FROM processed_scene
    UNION ALL
    SELECT content_type, validation_score, entities_count, processed_at FROM processed_dialogue
) all_content
GROUP BY content_type;

CREATE OR REPLACE VIEW validation_summary AS
SELECT
    content_type,
    COUNT(*) as total_validations,
    AVG(overall_score) as avg_score,
    COUNT(*) FILTER (WHERE is_valid) as valid_count,
    COUNT(*) FILTER (WHERE NOT is_valid) as invalid_count,
    AVG(validation_time) as avg_validation_time
FROM validation_results
GROUP BY content_type;

-- Functions for Data Integrity
CREATE OR REPLACE FUNCTION update_entity_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER entities_update_timestamp
    BEFORE UPDATE ON extracted_entities
    FOR EACH ROW
    EXECUTE FUNCTION update_entity_timestamp();

-- Sample Data for Testing (Optional)
-- INSERT INTO processed_worldview (original_id, cleaned_content, entities_count, content_hash)
-- VALUES ('test_world_001', '裂世九域是一个庞大的修仙世界，分为九个不同的域...', 5, 'abc123def456');

-- Comments for Documentation
COMMENT ON TABLE processed_worldview IS 'Stores processed worldview content with extracted entities and validation results';
COMMENT ON TABLE extracted_entities IS 'Master table for all extracted entities with canonical names and relationships';
COMMENT ON TABLE entity_mentions IS 'Individual mentions of entities within content, linked to master entities';
COMMENT ON TABLE validation_results IS 'Results of data quality validation for each processed record';
COMMENT ON TABLE pipeline_runs IS 'Tracking information for ETL pipeline execution runs';
COMMENT ON TABLE change_log IS 'Audit trail of all data changes for incremental processing';
COMMENT ON TABLE stream_events IS 'Real-time events processed through the streaming pipeline';