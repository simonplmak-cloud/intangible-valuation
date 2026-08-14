-- ============================================================================
-- V003: Commercial — Billing Tables
-- No seeding: plans are synced from Stripe Product/Price objects (real data).
-- ============================================================================

-- Plans (real pricing synced from Stripe; citation = stripe_price_id)
DEFINE TABLE plans SCHEMAFULL;
DEFINE FIELD name ON plans TYPE string ASSERT $value != NONE;
DEFINE FIELD price_monthly_cents ON plans TYPE int DEFAULT 0;
DEFINE FIELD stripe_price_id ON plans TYPE option<string>;
DEFINE FIELD features ON plans TYPE array DEFAULT [];
DEFINE FIELD quota_saved_valuations ON plans TYPE int DEFAULT -1;
DEFINE FIELD stripe_product_id ON plans TYPE option<string>;

-- Subscriptions
DEFINE TABLE subscriptions SCHEMAFULL;
DEFINE FIELD user_id ON subscriptions TYPE string ASSERT $value != NONE;
DEFINE FIELD plan_id ON subscriptions TYPE string ASSERT $value != NONE;
DEFINE FIELD status ON subscriptions TYPE string DEFAULT 'active' ASSERT $value IN ['active', 'past_due', 'canceled', 'trialing'];
DEFINE FIELD stripe_customer_id ON subscriptions TYPE string ASSERT $value != NONE;
DEFINE FIELD stripe_subscription_id ON subscriptions TYPE option<string>;
DEFINE FIELD current_period_end ON subscriptions TYPE option<datetime>;
DEFINE FIELD created_at ON subscriptions TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON subscriptions TYPE datetime DEFAULT time::now();

-- Usage (quota counters; real, increment-only)
DEFINE TABLE usage SCHEMAFULL;
DEFINE FIELD user_id ON usage TYPE string ASSERT $value != NONE;
DEFINE FIELD metric ON usage TYPE string ASSERT $value IN ['saved_valuations', 'pdf_exports'];
DEFINE FIELD count ON usage TYPE int DEFAULT 0 ASSERT $value >= 0;
DEFINE FIELD period_start ON usage TYPE datetime DEFAULT time::now();
DEFINE FIELD reset_at ON usage TYPE datetime DEFAULT time::now();

-- Webhook events (append-only; idempotent by stripe_event_id)
DEFINE TABLE webhook_events SCHEMAFULL;
DEFINE FIELD stripe_event_id ON webhook_events TYPE string ASSERT $value != NONE;
DEFINE FIELD type ON webhook_events TYPE string ASSERT $value != NONE;
DEFINE FIELD payload ON webhook_events TYPE object;
DEFINE FIELD processed_at ON webhook_events TYPE datetime DEFAULT time::now();

-- Consent (ToS/Privacy acceptance)
DEFINE TABLE consents SCHEMAFULL;
DEFINE FIELD user_id ON consents TYPE string ASSERT $value != NONE;
DEFINE FIELD terms_version ON consents TYPE string ASSERT $value != NONE;
DEFINE FIELD privacy_version ON consents TYPE string ASSERT $value != NONE;
DEFINE FIELD accepted_at ON consents TYPE datetime DEFAULT time::now();

-- Indexes
DEFINE INDEX idx_subscriptions_user ON subscriptions COLUMNS user_id UNIQUE;
DEFINE INDEX idx_subscriptions_customer ON subscriptions COLUMNS stripe_customer_id UNIQUE;
DEFINE INDEX idx_usage_user_metric ON usage COLUMNS user_id, metric UNIQUE;
DEFINE INDEX idx_webhook_event ON webhook_events COLUMNS stripe_event_id UNIQUE;
DEFINE INDEX idx_consents_user ON consents COLUMNS user_id UNIQUE;
