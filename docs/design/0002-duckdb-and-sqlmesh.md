# 0002: DuckDB + SQLMesh for the transform layer

**Day:** 2

## Decision
Transformations are SQL models managed by SQLMesh, run against DuckDB.

## Why
The workload here is single-writer, laptop-scale, and read-heavy — exactly what DuckDB is
for. Columnar-speed SQL with no server to stand up or babysit.

SQLMesh is the part I went back and forth on, since raw `.sql` files run by a shell script
would technically work too. What tipped it: `plan` shows you the actual diff of what a
change will do to downstream models *before* it touches anything, models can be unit
tested against fixtures instead of live data, and data-quality audits are just part of
the same workflow instead of a bolted-on second tool. That's a lot of infrastructure I'd
otherwise be writing myself, badly.

## Gotcha
Hit this within the first hour: `config.yaml`'s `database:` path is relative to the
process's working directory when SQLMesh runs — not to where the config file itself
lives. Cost me ten minutes of "why can't it find the db" before I realized it. Fix going
forward: every `sqlmesh` command in this repo is run from `sqlmesh/`, full stop, no
exceptions.

## Revisit if
Write volume or query concurrency ever outgrows what a single-writer engine can handle.
If that happens, only the engine underneath changes — the model layer itself (SQL +
SQLMesh) shouldn't need to be touched.
