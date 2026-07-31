import contextlib
from pathlib import Path

import duckdb
from dagster import AssetExecutionContext, Definitions, asset
from dagster_sqlmesh import SQLMeshContextConfig, SQLMeshResource, sqlmesh_assets

REPO_ROOT = Path(__file__).resolve().parents[3]
SQLMESH_PROJECT_PATH = REPO_ROOT / "sqlmesh"
WAREHOUSE_PATH = REPO_ROOT / "warehouse" / "meridian.duckdb"

sqlmesh_config = SQLMeshContextConfig(
    path=str(SQLMESH_PROJECT_PATH),
    gateway="local",
)


@asset
def observability_schema() -> None:
    """Ensures the `observability` schema exists in the warehouse.

    Nothing writes into it yet -- this just establishes the convention that
    Dagster-side observability tables live in their own schema, separate
    from SQLMesh-managed models.
    """
    con = duckdb.connect(str(WAREHOUSE_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS observability")
    con.close()


@sqlmesh_assets(environment="dev", config=sqlmesh_config)
def meridian_sqlmesh_assets(context: AssetExecutionContext, sqlmesh: SQLMeshResource):
    # config.yaml's `database: ../warehouse/...` is resolved relative to
    # wherever sqlmesh actually runs from -- same gotcha as day 2. Passing an
    # absolute `path=` to SQLMeshContextConfig doesn't change that, so we
    # scope a chdir to just this call.
    with contextlib.chdir(SQLMESH_PROJECT_PATH):
        yield from sqlmesh.run(context)


defs = Definitions(
    assets=[observability_schema, meridian_sqlmesh_assets],
    resources={"sqlmesh": SQLMeshResource(config=sqlmesh_config)},
)
