#!/usr/bin/env bash
# One-command boot: materialise the trivial SQLMesh model, then serve the
# Dagster UI. Idempotent - safe to run on every container start.
set -euo pipefail

cd /app/sqlmesh
uv run --project /app sqlmesh plan --auto-apply --no-prompts
cd /app

uv run --project /app python -c "
import duckdb
from pathlib import Path
p = Path('/app/warehouse/meridian.duckdb')
p.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(p))
con.execute('CREATE SCHEMA IF NOT EXISTS observability')
con.close()
print('observability schema ready')
"

exec uv run --project /app dagster dev -w /app/workspace.yaml -h 0.0.0.0 -p 3000
