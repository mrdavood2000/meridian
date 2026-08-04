from __future__ import annotations

import datetime as dt
import uuid
from pathlib import Path

import httpx
import pandas as pd

BASE_URL = "https://api.luchtmeetnet.nl/open_api"


def _client(client: httpx.Client | None) -> httpx.Client:
    return client or httpx.Client(base_url=BASE_URL, timeout=30)


def fetch_station_candidates(client: httpx.Client | None = None) -> list[dict]:
    client = _client(client)
    candidates: list[dict] = []
    page = 1
    while True:
        resp = client.get("/stations", params={"order_by": "number", "page": page})
        resp.raise_for_status()
        body = resp.json()
        for station in body["data"]:
            if "amsterdam" in station["location"].lower():
                candidates.append(station)
        pagination = body["pagination"]
        if pagination["current_page"] >= pagination["last_page"]:
            break
        page += 1
    return candidates


def fetch_station_detail(number: str, client: httpx.Client | None = None) -> dict:
    client = _client(client)
    resp = client.get(f"/stations/{number}")
    resp.raise_for_status()
    return resp.json()["data"]


def fetch_amsterdam_stations(client: httpx.Client | None = None) -> list[dict]:
    client = _client(client)
    candidates = fetch_station_candidates(client)
    print(f"{len(candidates)} candidates by location string match")
    confirmed = []
    for c in candidates:
        detail = fetch_station_detail(c["number"], client)
        if detail.get("municipality") == "Amsterdam":
            confirmed.append(detail)
        else:
            print(f"  dropped: {c['number']} {c['location']!r} -> municipality={detail.get('municipality')!r}")
    print(f"{len(confirmed)} confirmed by municipality")
    return confirmed


def fetch_measurements(
    station_numbers: list[str],
    start: dt.datetime,
    end: dt.datetime,
    client: httpx.Client | None = None,
) -> list[dict]:
    client = _client(client)
    rows: list[dict] = []
    for number in station_numbers:
        page = 1
        while True:
            resp = client.get(
                f"/stations/{number}/measurements",
                params={"start": start.isoformat(), "end": end.isoformat(), "page": page},
            )
            resp.raise_for_status()
            body = resp.json()
            for row in body["data"]:
                row["station_number"] = number
                rows.append(row)
            pagination = body["pagination"]
            if pagination["current_page"] >= pagination["last_page"]:
                break
            page += 1
    return rows


def _write_hive_parquet(df: pd.DataFrame, lake_root: Path, feed: str, date_col: str) -> None:
    if df.empty:
        return
    df = df.copy()
    df["_event_date"] = pd.to_datetime(df[date_col]).dt.date
    for event_date, group in df.groupby("_event_date"):
        out_dir = lake_root / f"source={feed}" / f"event_date={event_date}"
        out_dir.mkdir(parents=True, exist_ok=True)
        group.drop(columns=["_event_date"]).to_parquet(out_dir / f"part-{uuid.uuid4()}.parquet", index=False)


def land_stations(lake_root: Path) -> pd.DataFrame:
    df = pd.DataFrame(fetch_amsterdam_stations()).rename(columns={"number": "station_number"})
    df["ingested_at"] = dt.datetime.now(dt.timezone.utc)
    _write_hive_parquet(df, lake_root, "air_quality_stations", "ingested_at")
    return df


def land_measurements(
    lake_root: Path, station_numbers: list[str], start: dt.datetime, end: dt.datetime
) -> pd.DataFrame:
    df = pd.DataFrame(fetch_measurements(station_numbers, start, end))
    df["ingested_at"] = dt.datetime.now(dt.timezone.utc)
    _write_hive_parquet(df, lake_root, "air_quality_measurements", "timestamp_measured")
    return df
