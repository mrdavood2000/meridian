MODEL (
  name meta.heartbeat,
  kind FULL,
  audits (assert_heartbeat_is_ok),
  description 'Trivial model: proves the SQLMesh -> DuckDB wiring works end to end. Nothing real depends on this - it exists so CI has something to plan/test/audit from commit one.'
);

SELECT
  1 AS id,
  CURRENT_TIMESTAMP AS checked_at
