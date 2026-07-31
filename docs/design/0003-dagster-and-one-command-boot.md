# 0003 — Dagster for orchestration, `docker compose up` for one-command boot

**Date:** day 3

**Decision:** SQLMesh runs are wrapped as Dagster assets (via `dagster-sqlmesh`), and the whole stack boots with one `docker compose up --build`.

**Why Dagster.** The alternative was "just use SQLMesh's own built-in scheduler and skip an orchestrator entirely." Dagster earns its place once there's real lineage across multiple feeds to see and real ingestion jobs to schedule independently of the transform layer — neither exists yet at day 3, which is exactly why it's introduced now, deliberately early: if the integration was going to have sharp edges, better to find them in week one than in week three when a broken wiring would block everything built on top of it. It did have one: see the gotcha below.

**Why `docker compose up` as the only documented way to boot.** One command, one true way to run this — no "works if you remember to also do X first" tribal knowledge.

**A real gotcha, hit immediately:** the exact same relative-path issue from day 2
(`config.yaml`'s `database:` path resolves against the process's *working directory*) resurfaces inside the Dagster asset, because Dagster runs `meridian_sqlmesh_assets` with the repo root as `cwd`, not `sqlmesh/`. Fixed by wrapping the SQLMesh call in `contextlib.chdir(SQLMESH_PROJECT_PATH)` — the same fix in spirit as "every SQLMesh CLI command runs from `sqlmesh/`," just applied at the one call site that isn't a CLI invocation.

**Revisit if:** true sub-minute polling cadences are ever needed — Dagster's cron-based `ScheduleDefinition` has no sub-minute granularity; that would need a sensor/daemon loop instead.
