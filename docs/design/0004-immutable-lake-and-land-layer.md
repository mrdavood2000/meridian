# 0004: An immutable, Hive-partitioned lake as the land layer

**Day:** 4

## Decision
Every feed's land function writes the raw API response, verbatim, to
`lake/source=<feed>/event_date=<date>/part-*.parquet` — one new file per poll. Nothing is
ever overwritten or edited in place.

## Why
The whole point is that everything downstream should be recomputable from the lake. If
that holds, a bug in the conform or model layer is just a bug — fix the logic and rerun
it — never lost data. Parquet plus DuckDB gives real columnar read speed with zero server
to run, and Hive-style partitioning (`source=`/`event_date=` baked into the path) is what
lets the query engine skip entire files without even opening them.

## A real finding, not just a gotcha
While scoping this feed down to Amsterdam I wrote what looked like an obviously correct
filter: does the station's `location` field contain "amsterdam"? It does — for a station
called "Den Haag-Amsterdamse Veerkade," which is in The Hague, not Amsterdam. I only
caught it by cross-checking against the API's own `municipality` field, which correctly
reports `'s-Gravenhage` for that station.

Nothing wrong with the API here — the lesson is more general than that. A filter that
looks self-evidently right is still worth checking against real output before trusting
it, especially the first time it's written. This one would've silently polluted the
Amsterdam slice with a Hague station indefinitely.

## Revisit if
Land ever needs to stop being one-file-per-poll — say, a feed with a much higher poll
frequency starts generating too many tiny files. The fix there is a compaction step
downstream, not a change to land's append-only contract.
