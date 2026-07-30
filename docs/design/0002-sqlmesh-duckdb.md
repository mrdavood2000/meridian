# 0002 — DuckDB + SQLMesh for the transform layer

**Date:** day 2

**Decision:** transformations are SQL models managed by SQLMesh, executed against DuckDB.

**Why.** This is a single-writer, laptop-scale, read-heavy analytical workload — DuckDB gives
columnar-speed SQL over that with zero server to run or operate. SQLMesh adds what raw SQL scripts
don't: versioned models, environment diffing (`plan` shows exactly what would change before it
changes anything), fixture-based unit tests independent of live data, and named data-quality
audits that run as part of the same workflow instead of a separate tool.

**A real gotcha, hit immediately:** `config.yaml`'s `database:` path is relative to the *process's
working directory* when SQLMesh runs, not to the config file's own location. Every `sqlmesh`
command in this repo runs with `sqlmesh/` as the working directory for exactly this reason.

**Revisit if:** the write volume or query concurrency ever outgrows a single-writer engine — the
model layer (SQL + SQLMesh) doesn't need to change, only the engine underneath it would.
