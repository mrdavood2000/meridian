AUDIT (
  name assert_heartbeat_is_ok
);

SELECT *
FROM meta.heartbeat
WHERE id IS NULL
   OR checked_at IS NULL
