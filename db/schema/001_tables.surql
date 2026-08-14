-- ============================================================================
-- V001: Tables — Intangible Valuation Platform
-- ============================================================================

-- Users (mirrors Clerk identity)
DEFINE TABLE users SCHEMAFULL;
DEFINE FIELD email ON users TYPE string ASSERT $value != NONE;
DEFINE FIELD name ON users TYPE string;
DEFINE FIELD role ON users TYPE string DEFAULT 'public' ASSERT $value IN ['public', 'auditor', 'admin'];
DEFINE FIELD created_at ON users TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON users TYPE datetime DEFAULT time::now();
DEFINE FIELD subscription_tier ON users TYPE string DEFAULT 'free' ASSERT $value IN ['free', 'pro', 'enterprise'];
DEFINE FIELD organization ON users TYPE option<string>;
DEFINE FIELD avatar_url ON users TYPE option<string>;

-- Valuations
DEFINE TABLE valuations SCHEMAFULL;
DEFINE FIELD user_id ON valuations TYPE string ASSERT $value != NONE;
DEFINE FIELD method ON valuations TYPE string ASSERT $value != NONE;
DEFINE FIELD category ON valuations TYPE string ASSERT $value != NONE;
DEFINE FIELD asset_type ON valuations TYPE option<string>;
DEFINE FIELD business_stage ON valuations TYPE option<string>;
DEFINE FIELD inputs ON valuations TYPE object ASSERT $value != NONE;
DEFINE FIELD result_value ON valuations TYPE number ASSERT $value != NONE;
DEFINE FIELD formula_reference ON valuations TYPE string ASSERT $value != NONE;
DEFINE FIELD steps ON valuations TYPE option<array>;
DEFINE FIELD assumptions ON valuations TYPE option<array>;
DEFINE FIELD pv_before_tab ON valuations TYPE option<number>;
DEFINE FIELD tab_factor ON valuations TYPE option<number>;
DEFINE FIELD created_at ON valuations TYPE datetime DEFAULT time::now();
DEFINE FIELD is_favorite ON valuations TYPE bool DEFAULT false;

-- Benchmark data
DEFINE TABLE benchmarks SCHEMAFULL;
DEFINE FIELD category ON benchmarks TYPE string ASSERT $value IN ['royalty_rate', 'discount_rate', 'useful_life', 'growth_rate'];
DEFINE FIELD business_stage ON benchmarks TYPE string ASSERT $value IN ['startup', 'growth', 'mature'];
DEFINE FIELD asset_type ON benchmarks TYPE string DEFAULT 'all';
DEFINE FIELD industry ON benchmarks TYPE string DEFAULT 'all';
DEFINE FIELD metric_name ON benchmarks TYPE string ASSERT $value != NONE;
DEFINE FIELD value ON benchmarks TYPE number ASSERT $value != NONE;
DEFINE FIELD unit ON benchmarks TYPE option<string>;
DEFINE FIELD p25 ON benchmarks TYPE option<number>;
DEFINE FIELD p75 ON benchmarks TYPE option<number>;
DEFINE FIELD source ON benchmarks TYPE string ASSERT $value != NONE;
DEFINE FIELD source_url ON benchmarks TYPE option<string>;
DEFINE FIELD last_updated ON benchmarks TYPE datetime DEFAULT time::now();

-- Method catalog
DEFINE TABLE method_catalog SCHEMAFULL;
DEFINE FIELD slug ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD name ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD category ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD subcategory ON method_catalog TYPE option<string>;
DEFINE FIELD asset_types ON method_catalog TYPE option<array>;
DEFINE FIELD business_stages ON method_catalog TYPE option<array>;
DEFINE FIELD description ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD formula_tex ON method_catalog TYPE option<string>;
DEFINE FIELD textbook_reference ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD parameters ON method_catalog TYPE array ASSERT array::len($value) > 0;
DEFINE FIELD python_function ON method_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD mcp_tool_name ON method_catalog TYPE option<string>;
DEFINE FIELD skill_reference ON method_catalog TYPE option<string>;
DEFINE FIELD complexity ON method_catalog TYPE string DEFAULT 'basic' ASSERT $value IN ['basic', 'intermediate', 'advanced'];
DEFINE FIELD is_active ON method_catalog TYPE bool DEFAULT true;

-- API metrics
DEFINE TABLE api_metrics SCHEMAFULL;
DEFINE FIELD endpoint ON api_metrics TYPE string ASSERT $value != NONE;
DEFINE FIELD method ON api_metrics TYPE string ASSERT $value != NONE;
DEFINE FIELD user_id ON api_metrics TYPE option<string>;
DEFINE FIELD status_code ON api_metrics TYPE number ASSERT $value != NONE;
DEFINE FIELD duration_ms ON api_metrics TYPE number ASSERT $value != NONE;
DEFINE FIELD is_cold_start ON api_metrics TYPE bool DEFAULT false;
DEFINE FIELD timestamp ON api_metrics TYPE datetime DEFAULT time::now();
DEFINE FIELD error_message ON api_metrics TYPE option<string>;

-- Skills catalog
DEFINE TABLE skills_catalog SCHEMAFULL;
DEFINE FIELD slug ON skills_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD name ON skills_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD description ON skills_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD category ON skills_catalog TYPE option<string>;
DEFINE FIELD markdown_path ON skills_catalog TYPE string ASSERT $value != NONE;
DEFINE FIELD mcp_tools_required ON skills_catalog TYPE option<array>;
DEFINE FIELD is_active ON skills_catalog TYPE bool DEFAULT true;
