# Meridian

A self-auditing view of how Amsterdam moves and breathes.

Live Amsterdam / Netherlands open-data feeds — public transport, road traffic, air quality, civic
reports — landed immutably, conformed onto one event-time clock (UTC) and one spatial grid (H3
hexagons), modelled bitemporally so the system can answer both "what did we believe on the day?"
and "what do we now know was true?", served as tested tables, and checked continuously by a
monitoring layer built to catch the failures pipelines actually die of: the silent ones.

## Status

Being built in the open, one day at a time — each day is one pull request, with a short design note in [`docs/design/`](docs/design/) for every decision that wasn't obvious.

| Day | What landed |
|---|---|
| 1 | Project scaffolding: `uv`, `src/` layout, CI, lint, the secrets convention |
| 2 | SQLMesh + DuckDB: first model, test and audit, wired into CI |
| 3 | Dagster orchestration (`dagster-sqlmesh`) and one-command Docker boot |
| 4 | First real feed: Amsterdam air quality (Luchtmeetnet) landed immutably in the lake |

Next: conform the air-quality data onto the UTC clock and the H3 grid, then the bitemporal model, then the other three feeds and the monitoring layer.

## Stack

Python 3.12 · `uv` · DuckDB · SQLMesh · Dagster · GitHub Actions CI.

## Run it

Requires Docker.

```bash
cp .env.example .env
docker compose up --build
```

Opens the Dagster UI at <http://localhost:3000>. On a clean clone there's no real data yet.

### Without Docker

```bash
uv sync
cd sqlmesh && uv run --project .. sqlmesh plan --auto-apply --no-prompts && cd ..
uv run dagster dev -w workspace.yaml -h 0.0.0.0 -p 3000
```

### Tests

```bash
uv run pytest
cd sqlmesh && uv run --project .. sqlmesh test && uv run --project .. sqlmesh audit
```

## Design notes

See [`docs/design/`](docs/design/) for short, dated notes on the decisions that weren't obvious
at the time.
