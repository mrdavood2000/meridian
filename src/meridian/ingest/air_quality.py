"""Land layer for Luchtmeetnet air quality: poll the live, keyless API and
write the response verbatim to the Parquet lake. No filtering logic beyond
scoping to Amsterdam happens here - land captures faithfully, nothing else.

Verified live against api.luchtmeetnet.nl: keyless, JSON, page-based
pagination via a `pagination` envelope. `/open_api/measurements` requires
explicit `start`/`end` query params.

Scoping to Amsterdam is two steps, not one, because a naive substring match
on the station `location` string produces a real false positive: a station
named "Den Haag-Amsterdamse Veerkade" matches "amsterdam" but its authoritative
`municipality` field is "'s-Gravenhage" (The Hague), not Amsterdam. The cheap
substring match is only ever used to shortlist candidates before the more
expensive per-station detail call, which carries the real `municipality`
field used for the actual filter.
"""

from __future__ import annotations

import datetime as dt
import typing as t
import uuid
from pathlib import Path

import httpx
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

BASE_URL = "https://api.luchtmeetnet.nl/open_api"
STATIONS_URL = f"{BASE_URL}/stations"
MEASUREMENTS_URL = f"{BASE_URL}/measurements"

TARGET_MUNICIPALITY = "Amsterdam"


def _paginate(client: httpx.Client, url: str, params: dict) -> list[dict]:
    records: list[dict] = []
    page = 1
    while True:
        resp = client.get(url, params={**params, "page": page})
        resp.raise_for_status()
        body = resp.json()
        records.extend(body["data"])
        pagination = body["pagination"]
        if pagination["current_page"] >= pagination["last_page"]:
            break
        page += 1
    return records


def fetch_station_candidates(client: httpx.Client) -> list[str]:
    """Cheap pre-filter: every station whose location string mentions
    Amsterdam. Includes false positives - see module docstring.
    """
    all_stations = _paginate(client, STATIONS_URL, {"order_by": "number"})
    return [
        s["number"] for s in all_stations if TARGET_MUNICIPALITY.lower() in s["location"].lower()
    ]


def fetch_station_detail(client: httpx.Client, station_number: str) -> dict:
    resp = client.get(f"{STATIONS_URL}/{station_number}")
    resp.raise_for_status()
    data = resp.json()["data"]
    coords = data["geometry"]["coordinates"]  # [lon, lat]
    return {
        "station_number": station_number,
        "location": data["location"],
        "municipality": data.get("municipality"),
        "lon": coords[0],
        "lat": coords[1],
    }


def fetch_amsterdam_stations(client: t.Optional[httpx.Client] = None) -> pd.DataFrame:
    """The authoritative-municipality-filtered Amsterdam station set, live."""
    owns_client = client is None
    client = client or httpx.Client(timeout=30.0)
    try:
        candidates = fetch_station_candidates(client)
        details = [fetch_station_detail(client, number) for number in candidates]
    finally:
        if owns_client:
            client.close()

    df = pd.DataFrame(details)
    if df.empty:
        return df
    return df[df["municipality"] == TARGET_MUNICIPALITY].reset_index(drop=True)


def fetch_measurements(
    station_numbers: list[str],
    start: dt.datetime,
    end: dt.datetime,
    client: t.Optional[httpx.Client] = None,
) -> pd.DataFrame:
    """Every measurement for the given stations in [start, end), verbatim."""
    owns_client = client is None
    client = client or httpx.Client(timeout=30.0)
    try:
        rows: list[dict] = []
        for station_number in station_numbers:
            rows.extend(
                _paginate(
                    client,
                    MEASUREMENTS_URL,
                    {
                        "station_number": station_number,
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                        "order_by": "timestamp_measured",
                    },
                )
            )
    finally:
        if owns_client:
            client.close()
    return pd.DataFrame(rows, columns=["station_number", "value", "timestamp_measured", "formula"])


def _write_partition(df: pd.DataFrame, event_date: dt.date, lake_root: Path, source: str) -> Path:
    partition_dir = lake_root / f"source={source}" / f"event_date={event_date.isoformat()}"
    partition_dir.mkdir(parents=True, exist_ok=True)
    file_path = partition_dir / f"part-{uuid.uuid4().hex}.parquet"
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), file_path)
    return file_path


def land_stations(lake_root: Path, client: t.Optional[httpx.Client] = None) -> pd.DataFrame:
    """Poll station metadata and land it, verbatim plus ingest metadata."""
    stations = fetch_amsterdam_stations(client=client)
    ingested_at = dt.datetime.now(dt.timezone.utc)
    stations["ingested_at"] = ingested_at
    if not stations.empty:
        _write_partition(stations, ingested_at.date(), lake_root, "air_quality_stations")
    return stations


def land_measurements(
    lake_root: Path,
    station_numbers: list[str],
    start: dt.datetime,
    end: dt.datetime,
    client: t.Optional[httpx.Client] = None,
) -> pd.DataFrame:
    """Poll measurements and land them verbatim, partitioned by the day the
    measurement actually happened - not the day it was polled - so a
    single land call can straddle a UTC midnight boundary correctly.
    """
    measurements = fetch_measurements(station_numbers, start, end, client=client)
    ingested_at = dt.datetime.now(dt.timezone.utc)
    if measurements.empty:
        return measurements

    measurements = measurements.copy()
    measurements["ingested_at"] = ingested_at
    measurements["event_date"] = pd.to_datetime(measurements["timestamp_measured"]).dt.date

    for event_date, group in measurements.groupby("event_date"):
        _write_partition(group.drop(columns=["event_date"]), event_date, lake_root, "air_quality")
    return measurements
