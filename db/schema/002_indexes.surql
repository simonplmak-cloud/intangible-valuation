-- ============================================================================
-- V001: Indexes
-- ============================================================================

-- Valuations: dashboard queries
DEFINE INDEX idx_valuations_user ON valuations COLUMNS user_id;
DEFINE INDEX idx_valuations_method ON valuations COLUMNS method;
DEFINE INDEX idx_valuations_created ON valuations COLUMNS created_at;

-- Benchmarks: fast defaults lookup
DEFINE INDEX idx_benchmarks_category_stage ON benchmarks COLUMNS category, business_stage;
DEFINE INDEX idx_benchmarks_asset ON benchmarks COLUMNS asset_type;
DEFINE INDEX idx_benchmarks_industry ON benchmarks COLUMNS industry;

-- Method catalog: slug lookup
DEFINE INDEX idx_method_slug ON method_catalog COLUMNS slug UNIQUE;
DEFINE INDEX idx_method_category ON method_catalog COLUMNS category;

-- API metrics: monitoring
DEFINE INDEX idx_metrics_endpoint ON api_metrics COLUMNS endpoint;
DEFINE INDEX idx_metrics_timestamp ON api_metrics COLUMNS timestamp;

-- Skills: slug lookup
DEFINE INDEX idx_skills_slug ON skills_catalog COLUMNS slug UNIQUE;

-- Users: email lookup
DEFINE INDEX idx_users_email ON users COLUMNS email UNIQUE;
