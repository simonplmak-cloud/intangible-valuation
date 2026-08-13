-- ============================================================================
-- V003: Commercial — Billing Permissions
-- ============================================================================

-- Plans: public read (pricing page); admin write (sync)
DEFINE TABLE plans PERMISSIONS
  FOR select FULL
  FOR create, update, delete WHERE $auth.role = 'admin';

-- Subscriptions: owner + admin read; system (webhook) writes
DEFINE TABLE subscriptions PERMISSIONS
  FOR select WHERE user_id = $auth.id OR $auth.role = 'admin'
  FOR create WHERE $auth.id IS NOT NONE
  FOR update WHERE $auth.role = 'admin'
  FOR delete WHERE $auth.role = 'admin';

-- Usage: owner + admin read; system writes
DEFINE TABLE usage PERMISSIONS
  FOR select WHERE user_id = $auth.id OR $auth.role = 'admin'
  FOR create FULL
  FOR update WHERE $auth.role = 'admin'
  FOR delete NONE;

-- Webhook events: admin only
DEFINE TABLE webhook_events PERMISSIONS
  FOR select WHERE $auth.role = 'admin'
  FOR create FULL
  FOR update, delete NONE;

-- Consent: owner + admin read; write at signup
DEFINE TABLE consents PERMISSIONS
  FOR select WHERE user_id = $auth.id OR $auth.role = 'admin'
  FOR create WHERE $auth.id IS NOT NONE
  FOR update, delete NONE;
