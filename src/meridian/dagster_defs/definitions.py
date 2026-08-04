"""Dagster asset graph.

`observability_schema` establishes an empty `observability` schema in the
warehouse before any check ever writes into it - the convention exists
before there's anything to check.

`meridian_sqlmesh_assets` wraps the whole SQLMesh project (every model in
`sqlmesh/`) as a single Dagster asset via the `dagster-sqlmesh` integration,
so SQLMesh runs show up in the Dagster asset graph instead of being an
invisible side process.
"""

import contextlib
import datetime as dt
from pathlib import Path

import duckdb
from dagster import (
    AssetExecutionContext,
    Definitions,
    ScheduleDefinition,
    asset,
    define_asset_job,
)
from dagster_sqlmesh import SQLMeshContextConfig, SQLMeshResource, sqlmesh_assets

from meridian.ingest.air_quality import land_measurements, land_stations

REPO_ROOT = Path(__file__).resolve().parents[3]
SQLMESH_PROJECT_PATH = str(REPO_ROOT / "sqlmesh")
WAREHOUSE_PATH = REPO_ROOT / "warehouse" / "meridian.duckdb"
LAKE_ROOT = REPO_ROOT / "lake"

sqlmesh_config = SQLMeshContextConfig(path=SQLMESH_PROJECT_PATH, gateway="local")


@asset(
    description=(
        "Ensures the `observability` schema exists in the DuckDB warehouse. "
        "Empty for now - no check writes into it yet."
    )
)
def observability_schema() -> None:
    WAREHOUSE_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE_PATH))
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS observability")
    finally:
        con.close()


@sqlmesh_assets(environment="prod", config=sqlmesh_config)
def meridian_sqlmesh_assets(context: AssetExecutionContext, sqlmesh: SQLMeshResource):
    # config= is required here, not just on the decorator above - the decorator
    # only shapes the asset graph when definitions load; the resource still
    # needs it again at the point it actually runs.
    #
    # contextlib.chdir into sqlmesh/ for the same reason `sqlmesh` CLI commands
    # always run with sqlmesh/ as cwd (see docs/design/0002): config.yaml's
    # `database: ../warehouse/meridian.duckdb` is relative to the *process's*
    # working directory, and this asset otherwise runs with cwd = repo root.
    # Safe to scope with a plain chdir here (not a global one) because
    # Dagster's default executor runs each step in its own subprocess.
    with contextlib.chdir(SQLMESH_PROJECT_PATH):
        yield from sqlmesh.run(context, config=sqlmesh_config, environment="prod")


@asset(
    group_name="land_air_quality",
    description="Polls Luchtmeetnet for the live Amsterdam station list and lands it verbatim.",
)
def land_air_quality_stations() -> int:
    stations = land_stations(LAKE_ROOT)
    return len(stations)


@asset(
    group_name="land_air_quality",
    deps=[land_air_quality_stations],
    description=(
        "Polls Luchtmeetnet for the last 25 hours of measurements at every landed Amsterdam "
        "station. The 25h window (not 1h, to match an hourly schedule) deliberately overlaps "
        "the previous run so a missed schedule tick doesn't create a silent gap."
    ),
)
def land_air_quality_measurements() -> int:
    stations = land_stations(LAKE_ROOT)  # re-fetched live, not passed through Dagster IO
    now = dt.datetime.now(dt.UTC)
    start = now - dt.timedelta(hours=25)
    measurements = land_measurements(LAKE_ROOT, stations["station_number"].tolist(), start, now)
    return len(measurements)


land_air_quality_job = define_asset_job(
    "land_air_quality_job",
    selection=[land_air_quality_stations, land_air_quality_measurements],
)
land_air_quality_schedule = ScheduleDefinition(
    job=land_air_quality_job,
    cron_schedule="5 * * * *",  # hourly, 5 minutes past - Luchtmeetnet publishes hourly
)


defs = Definitions(
    assets=[
        observability_schema,
        meridian_sqlmesh_assets,
        land_air_quality_stations,
        land_air_quality_measurements,
    ],
    resources={"sqlmesh": SQLMeshResource(config=sqlmesh_config)},
    schedules=[land_air_quality_schedule],
)
