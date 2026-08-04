# 0004 — An immutable, Hive-partitioned lake as the land layer

**Date:** day 4

**Decision:** every feed's land function writes the raw API response, verbatim, to
`lake/source=<feed>/event_date=<date>/part-*.parquet` — one new file per poll, never overwritten,
never edited in place.

**Why.** If every downstream layer can be recomputed from the lake, a bug in conform/model logic
is a bug you can *fix and rerun*, not data you've lost. Parquet + DuckDB reads columnar data at
real speed with zero server to operate; Hive partitioning (`source=`/`event_date=` in the path
itself) is what lets a query engine skip whole files without opening them.

**A real, live finding while scoping this feed to Amsterdam:** a naive substring match on the
station `location` field ("does it contain 'amsterdam'?") produces a genuine false positive - a
station called "Den Haag-Amsterdamse Veerkade" matches, but it's in The Hague, not Amsterdam
(confirmed against the API's own authoritative `municipality` field, which reports
`'s-Gravenhage` for that station). The lesson isn't about this specific API - it's that a filter
that *looks* obviously correct is worth verifying against real output before trusting it,
especially the first time you write it.

**Revisit if:** land ever needs to *not* be one-file-per-poll (e.g. a feed with extremely high
poll frequency generating too many tiny files) - the fix would be a compaction step downstream,
not changing land's own append-only contract.
