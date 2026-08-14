-- ============================================================================
-- V001: Graph Relations
-- ============================================================================

-- Audit trail: User → Valuation (who calculated what)
DEFINE TABLE audit_trail SCHEMAFULL TYPE RELATION IN users OUT valuations;
DEFINE FIELD action ON audit_trail TYPE string DEFAULT 'created' ASSERT $value IN ['created', 'exported', 'shared', 'deleted'];
DEFINE FIELD ip_address ON audit_trail TYPE option<string>;
DEFINE FIELD user_agent ON audit_trail TYPE option<string>;
DEFINE FIELD created_at ON audit_trail TYPE datetime DEFAULT time::now();
DEFINE FIELD metadata ON audit_trail TYPE option<object>;

-- Index on audit trail for dashboard queries
DEFINE INDEX idx_audit_trail_in ON audit_trail COLUMNS in;
DEFINE INDEX idx_audit_trail_out ON audit_trail COLUMNS out;
DEFINE INDEX idx_audit_trail_time ON audit_trail COLUMNS created_at;
