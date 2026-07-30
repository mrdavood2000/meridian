# Meridian

*A self-auditing view of how Amsterdam moves and breathes.*

Live Amsterdam / Netherlands open-data feeds — public transport, road traffic, air quality, civic reports — landed immutably, conformed onto a single event-time clock (UTC) and a single spatial grid (H3 hexagons), modeled bitemporally so the system can answer both "what did we believe on the day?" and "what do we now know was true?", served as tested tables, and checked continuously by a monitoring layer built to catch the failures pipelines actually die of: the silent ones.

## Status

Early scaffolding. Nothing real lands yet.

## Stack

Python 3.12 · `uv` · DuckDB · SQLMesh · Dagster · GitHub Actions CI

## Run it

```bash
uv sync
uv run pytest
```

## Design notes

See [`docs/design/`](docs/design/) for short, dated notes on the decisions that weren't obvious at the time.
