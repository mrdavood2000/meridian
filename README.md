# Meridian

A self-auditing view of how Amsterdam moves and breathes.

Live Amsterdam / Netherlands open-data feeds — public transport, road traffic, air quality, civic
reports — landed immutably, conformed onto one event-time clock (UTC) and one spatial grid (H3
hexagons), modelled bitemporally so the system can answer both "what did we believe on the day?"
and "what do we now know was true?", served as tested tables, and checked continuously by a
monitoring layer built to catch the failures pipelines actually die of: the silent ones.

## Status

Early scaffolding. Nothing real lands yet.

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
