# lake/

Raw, immutable, append-only landed data, hive-partitioned:

    lake/source=<feed>/event_date=<date>/part-<uuid>.parquet

Directory structure is tracked in git; the `.parquet` files inside are not.
