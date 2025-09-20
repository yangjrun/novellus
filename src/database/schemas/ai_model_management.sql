-- AI Model Management System Schema
-- Version: 1.0.0
-- Description: Database schema for AI model management, request tracking, and performance monitoring

-- Extension for UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types for model providers and status
CREATE TYPE model_provider AS ENUM ('openai', 'anthropic', 'ollama', 'azure', 'google', 'cohere', 'huggingface');
CREATE TYPE model_status AS ENUM ('active', 'inactive', 'maintenance', 'deprecated', 'error');
CREATE TYPE request_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'timeout', 'cached');
CREATE TYPE model_capability AS ENUM ('chat', 'completion', 'embedding', 'image', 'audio', 'code', 'function_calling');

-- AI Models Configuration Table
CREATE TABLE ai_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider model_provider NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(100),
    display_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- API Configuration
    api_endpoint VARCHAR(500),
    api_key_encrypted TEXT, -- Store encrypted API keys
    api_key_hint VARCHAR(20), -- Last 4 characters for identification
    custom_headers JSONB DEFAULT '{}',

    -- Model Parameters
    max_tokens INTEGER DEFAULT 4096,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    top_p DECIMAL(3,2) DEFAULT 1.0,
    frequency_penalty DECIMAL(3,2) DEFAULT 0.0,
    presence_penalty DECIMAL(3,2) DEFAULT 0.0,
    default_params JSONB DEFAULT '{}',

    -- Capabilities
    capabilities model_capability[] DEFAULT ARRAY['chat', 'completion'],
    supports_streaming BOOLEAN DEFAULT true,
    supports_function_calling BOOLEAN DEFAULT false,
    context_window INTEGER DEFAULT 4096,

    -- Cost Configuration
    input_token_cost DECIMAL(10,6), -- Cost per 1K tokens
    output_token_cost DECIMAL(10,6), -- Cost per 1K tokens
    monthly_quota DECIMAL(10,2),
    daily_quota DECIMAL(10,2),

    -- Status and Priority
    status model_status DEFAULT 'active',
    priority INTEGER DEFAULT 100, -- Higher number = higher priority for load balancing
    health_score DECIMAL(5,2) DEFAULT 100.0, -- 0-100 health score

    -- Rate Limiting
    requests_per_minute INTEGER DEFAULT 60,
    requests_per_hour INTEGER DEFAULT 3600,
    concurrent_requests INTEGER DEFAULT 10,

    -- Metadata
    tags VARCHAR(100)[] DEFAULT ARRAY[]::VARCHAR[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE,

    UNIQUE(provider, model_name, model_version)
);

-- AI Request Tracking Table
CREATE TABLE ai_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ai_models(id) ON DELETE CASCADE,

    -- Request Information
    request_type VARCHAR(50) NOT NULL, -- 'chat', 'completion', 'embedding', etc.
    prompt TEXT,
    messages JSONB, -- For chat completions
    parameters JSONB DEFAULT '{}',

    -- Response Information
    response TEXT,
    response_metadata JSONB DEFAULT '{}',
    status request_status DEFAULT 'pending',
    error_message TEXT,
    error_code VARCHAR(100),

    -- Token Usage
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,

    -- Performance Metrics
    latency_ms INTEGER, -- Total request time in milliseconds
    time_to_first_token_ms INTEGER, -- For streaming responses
    processing_time_ms INTEGER,

    -- Cost Tracking
    estimated_cost DECIMAL(10,6),
    actual_cost DECIMAL(10,6),

    -- Cache Information
    cache_hit BOOLEAN DEFAULT false,
    cache_key VARCHAR(255),

    -- Context Information
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    project_id VARCHAR(255),
    workflow_id VARCHAR(255),
    parent_request_id UUID,

    -- Metadata
    tags VARCHAR(100)[] DEFAULT ARRAY[]::VARCHAR[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Indexes for common queries
    INDEX idx_ai_requests_model_id (model_id),
    INDEX idx_ai_requests_status (status),
    INDEX idx_ai_requests_created_at (created_at DESC),
    INDEX idx_ai_requests_session_id (session_id),
    INDEX idx_ai_requests_cache_key (cache_key)
);

-- AI Response Cache Table
CREATE TABLE ai_response_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    model_id UUID REFERENCES ai_models(id) ON DELETE CASCADE,

    -- Request Information
    request_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of normalized request
    prompt TEXT,
    messages JSONB,
    parameters JSONB DEFAULT '{}',

    -- Response Information
    response TEXT NOT NULL,
    response_metadata JSONB DEFAULT '{}',

    -- Embedding for Semantic Search
    embedding VECTOR(1536), -- For semantic similarity search

    -- Usage Statistics
    hit_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- TTL Management
    expires_at TIMESTAMP WITH TIME ZONE,
    is_permanent BOOLEAN DEFAULT false,

    -- Quality Metrics
    confidence_score DECIMAL(3,2), -- 0-1 confidence in cache validity
    relevance_score DECIMAL(3,2), -- 0-1 relevance for semantic cache

    -- Metadata
    tags VARCHAR(100)[] DEFAULT ARRAY[]::VARCHAR[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_cache_request_hash (request_hash),
    INDEX idx_cache_expires_at (expires_at),
    INDEX idx_cache_hit_count (hit_count DESC),
    INDEX idx_cache_embedding (embedding) -- For vector similarity search
);

-- Model Performance Metrics Table
CREATE TABLE model_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ai_models(id) ON DELETE CASCADE,

    -- Time Window
    metric_date DATE NOT NULL,
    metric_hour INTEGER CHECK (metric_hour >= 0 AND metric_hour <= 23),

    -- Request Statistics
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    cached_requests INTEGER DEFAULT 0,
    timeout_requests INTEGER DEFAULT 0,

    -- Token Usage
    total_prompt_tokens BIGINT DEFAULT 0,
    total_completion_tokens BIGINT DEFAULT 0,

    -- Performance Metrics
    avg_latency_ms DECIMAL(10,2),
    p50_latency_ms DECIMAL(10,2),
    p95_latency_ms DECIMAL(10,2),
    p99_latency_ms DECIMAL(10,2),
    max_latency_ms DECIMAL(10,2),
    min_latency_ms DECIMAL(10,2),

    -- Cost Metrics
    total_cost DECIMAL(10,4) DEFAULT 0,
    avg_cost_per_request DECIMAL(10,6),

    -- Error Rates
    error_rate DECIMAL(5,2), -- Percentage
    timeout_rate DECIMAL(5,2), -- Percentage

    -- Cache Performance
    cache_hit_rate DECIMAL(5,2), -- Percentage
    cache_savings DECIMAL(10,4), -- Cost saved from cache hits

    -- Health Metrics
    availability DECIMAL(5,2), -- Percentage uptime
    health_score DECIMAL(5,2), -- 0-100 composite health score

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(model_id, metric_date, metric_hour),
    INDEX idx_metrics_model_date (model_id, metric_date DESC),
    INDEX idx_metrics_health_score (health_score DESC)
);

-- Model Load Balancing Rules Table
CREATE TABLE load_balancing_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,

    -- Rule Configuration
    routing_strategy VARCHAR(50) NOT NULL, -- 'round_robin', 'weighted', 'least_latency', 'cost_optimized', 'priority'
    model_pool UUID[] NOT NULL, -- Array of model IDs in the pool

    -- Weight Configuration (for weighted routing)
    model_weights JSONB DEFAULT '{}', -- {"model_id": weight}

    -- Conditions
    apply_conditions JSONB DEFAULT '{}', -- Conditions when this rule applies
    fallback_model_id UUID REFERENCES ai_models(id),

    -- Performance Thresholds
    max_latency_threshold_ms INTEGER,
    min_health_score DECIMAL(5,2) DEFAULT 70.0,

    -- Cost Optimization
    prefer_cached_responses BOOLEAN DEFAULT true,
    cost_optimization_level INTEGER DEFAULT 5, -- 0-10, higher = more aggressive cost optimization

    -- Status
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 100,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API Key Management Table (for secure storage)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ai_models(id) ON DELETE CASCADE,

    -- Key Information
    key_name VARCHAR(255) NOT NULL,
    encrypted_key TEXT NOT NULL, -- Encrypted with application key
    key_hint VARCHAR(20), -- Last 4 chars for identification

    -- Usage Limits
    monthly_limit DECIMAL(10,2),
    daily_limit DECIMAL(10,2),
    current_month_usage DECIMAL(10,2) DEFAULT 0,
    current_day_usage DECIMAL(10,2) DEFAULT 0,

    -- Validity
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_rotated_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(model_id, key_name)
);

-- Request Queue Table (for async processing)
CREATE TABLE request_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ai_models(id),

    -- Request Details
    request_data JSONB NOT NULL,
    priority INTEGER DEFAULT 5, -- 0-10, higher = higher priority

    -- Status
    status VARCHAR(50) DEFAULT 'queued', -- 'queued', 'processing', 'completed', 'failed'
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Scheduling
    scheduled_at TIMESTAMP WITH TIME ZONE,
    processing_started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Error Handling
    last_error TEXT,
    error_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_queue_status_priority (status, priority DESC),
    INDEX idx_queue_scheduled_at (scheduled_at)
);

-- Create update trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ai_models_updated_at BEFORE UPDATE ON ai_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_response_cache_updated_at BEFORE UPDATE ON ai_response_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_model_performance_metrics_updated_at BEFORE UPDATE ON model_performance_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_load_balancing_rules_updated_at BEFORE UPDATE ON load_balancing_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for monitoring
CREATE VIEW active_models_overview AS
SELECT
    m.id,
    m.provider,
    m.model_name,
    m.display_name,
    m.status,
    m.health_score,
    COUNT(DISTINCT r.id) as requests_24h,
    AVG(r.latency_ms) as avg_latency_24h,
    SUM(r.estimated_cost) as cost_24h
FROM ai_models m
LEFT JOIN ai_requests r ON m.id = r.model_id
    AND r.created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
WHERE m.status = 'active'
GROUP BY m.id, m.provider, m.model_name, m.display_name, m.status, m.health_score;

CREATE VIEW cache_performance AS
SELECT
    DATE(r.created_at) as date,
    COUNT(*) FILTER (WHERE r.cache_hit = true) as cache_hits,
    COUNT(*) FILTER (WHERE r.cache_hit = false) as cache_misses,
    ROUND(100.0 * COUNT(*) FILTER (WHERE r.cache_hit = true) / NULLIF(COUNT(*), 0), 2) as hit_rate,
    SUM(CASE WHEN r.cache_hit = true THEN r.estimated_cost ELSE 0 END) as cost_saved
FROM ai_requests r
WHERE r.created_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY DATE(r.created_at)
ORDER BY date DESC;

-- Sample data insertion for initial setup
INSERT INTO ai_models (provider, model_name, display_name, description, max_tokens, temperature, input_token_cost, output_token_cost, capabilities, supports_function_calling, context_window)
VALUES
    ('openai', 'gpt-4-turbo-preview', 'GPT-4 Turbo', 'Latest GPT-4 Turbo model with 128k context', 4096, 0.7, 0.01, 0.03, ARRAY['chat', 'completion', 'function_calling']::model_capability[], true, 128000),
    ('openai', 'gpt-4o', 'GPT-4o', 'Multimodal GPT-4 model', 4096, 0.7, 0.005, 0.015, ARRAY['chat', 'completion', 'image', 'function_calling']::model_capability[], true, 128000),
    ('openai', 'gpt-3.5-turbo', 'GPT-3.5 Turbo', 'Fast and efficient model', 4096, 0.7, 0.0005, 0.0015, ARRAY['chat', 'completion', 'function_calling']::model_capability[], true, 16385),
    ('anthropic', 'claude-3-opus-20240229', 'Claude 3 Opus', 'Most capable Claude model', 4096, 0.7, 0.015, 0.075, ARRAY['chat', 'completion']::model_capability[], false, 200000),
    ('anthropic', 'claude-3-sonnet-20240229', 'Claude 3 Sonnet', 'Balanced Claude model', 4096, 0.7, 0.003, 0.015, ARRAY['chat', 'completion']::model_capability[], false, 200000),
    ('anthropic', 'claude-3-haiku-20240307', 'Claude 3 Haiku', 'Fast Claude model', 4096, 0.7, 0.00025, 0.00125, ARRAY['chat', 'completion']::model_capability[], false, 200000);