MODEL (
  name meta.heartbeat,
  kind FULL,
  description 'Trivial constant-output model that proves the SQLMesh + DuckDB wiring works end to end.',
  audits (assert_heartbeat_is_ok)
);

SELECT
  1 AS id,
  CURRENT_TIMESTAMP AS checked_at
