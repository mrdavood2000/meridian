#!/usr/bin/env bash
set -euo pipefail

cd sqlmesh
uv run sqlmesh plan --auto-apply --no-prompts
cd ..

uv run python -c "
import duckdb
con = duckdb.connect('warehouse/meridian.duckdb')
con.execute('CREATE SCHEMA IF NOT EXISTS observability')
con.close()
"

exec uv run dagster dev -w workspace.yaml -h 0.0.0.0 -p 3000
