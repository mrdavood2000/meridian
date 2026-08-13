# The lake

Raw, landed data - the verbatim API response, plus ingest metadata (`ingested_at`), written once
and never edited or overwritten. Partitioned Hive-style: `source=<feed>/event_date=<date>/part-*.parquet`.

Nothing here is validated, filtered, or transformed beyond the minimal scoping decision each feed's
land function makes (e.g. "Amsterdam only"). If a later layer's logic is ever in doubt, this is the
ground truth to recompute from.

Contents are gitignored - only this file (the convention) is tracked.
