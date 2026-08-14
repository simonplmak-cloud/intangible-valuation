-- ============================================================================
-- V001: Record-Level Permissions
-- ============================================================================

-- Users can read/write their own records; admins have full access
DEFINE TABLE users PERMISSIONS
  FOR select WHERE id = $auth.id OR $auth.role = 'admin'
  FOR create FULL
  FOR update WHERE id = $auth.id OR $auth.role = 'admin'
  FOR delete WHERE $auth.role = 'admin';

-- Users can CRUD their own valuations; admins have full access
DEFINE TABLE valuations PERMISSIONS
  FOR select WHERE user_id = $auth.id OR $auth.role = 'admin'
  FOR create WHERE $auth.id IS NOT NONE
  FOR update WHERE user_id = $auth.id OR $auth.role = 'admin'
  FOR delete WHERE $auth.role = 'admin';

-- Audit trail: auditors and admins can read; system writes
DEFINE TABLE audit_trail PERMISSIONS
  FOR select WHERE $auth.role IN ['auditor', 'admin']
  FOR create WHERE $auth.role IN ['auditor', 'admin']
  FOR update, delete NONE;

-- Benchmarks: public read; admin write
DEFINE TABLE benchmarks PERMISSIONS
  FOR select FULL
  FOR create, update, delete WHERE $auth.role = 'admin';

-- Method catalog: public read; admin write
DEFINE TABLE method_catalog PERMISSIONS
  FOR select FULL
  FOR create, update, delete WHERE $auth.role = 'admin';

-- API metrics: admin only
DEFINE TABLE api_metrics PERMISSIONS
  FOR select WHERE $auth.role = 'admin'
  FOR create FULL
  FOR update, delete NONE;

-- Skills catalog: public read; admin write
DEFINE TABLE skills_catalog PERMISSIONS
  FOR select FULL
  FOR create, update, delete WHERE $auth.role = 'admin';
