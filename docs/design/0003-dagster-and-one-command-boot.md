# 0003: Dagster for orchestration, `docker compose up` for one-command boot

**Day:** 3

## Decision
SQLMesh runs are wrapped as Dagster assets via `dagster-sqlmesh`, and the whole stack
comes up with a single `docker compose up --build`.

## Why Dagster
I seriously considered skipping an orchestrator entirely and just leaning on SQLMesh's
own built-in scheduler. Dagster only really earns its keep once there's real lineage
across multiple feeds worth visualizing, and real ingestion jobs that need to run on
their own schedule, independent of the transform layer. Neither of those exists yet —
there's one feed and one schedule right now.

I brought it in anyway, on purpose, this early. If the `dagster-sqlmesh` integration was
going to have sharp edges, I'd rather hit them in week one, with nothing built on top of
it yet, than in week three when a broken wiring blocks everything downstream. It did have
an edge — see below.

## Why `docker compose up`
One command, one documented way to boot this thing. No tribal knowledge like "works, but
only if you also start X first and remember to export Y."

## Gotcha
Same relative-path problem as day 2, just wearing a different hat. `config.yaml`'s
`database:` path resolves against the process's working directory — and Dagster runs
`meridian_sqlmesh_assets` with the repo root as `cwd`, not `sqlmesh/`. So the fix from
0002 (always run from `sqlmesh/`) doesn't apply here, because this isn't a CLI
invocation. Ended up wrapping the SQLMesh call in `contextlib.chdir(SQLMESH_PROJECT_PATH)`
right at that one call site — same underlying fix, just applied where it's actually
needed this time.

## Revisit if
True sub-minute polling is ever needed. Dagster's `ScheduleDefinition` is cron-based and
has no sub-minute granularity, so that would mean reaching for a sensor/daemon loop
instead — not a small change, but not urgent today either.
