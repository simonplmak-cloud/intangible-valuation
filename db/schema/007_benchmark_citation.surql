-- ============================================================================
-- V003: Commercial — Benchmark citation chain (no seeding)
-- Every benchmark record carries a full citation chain
-- (source → author → date → url → specific reference).
-- ============================================================================

DEFINE FIELD author ON benchmarks TYPE option<string>;
DEFINE FIELD date ON benchmarks TYPE option<string>;
DEFINE FIELD ref ON benchmarks TYPE option<string>;
