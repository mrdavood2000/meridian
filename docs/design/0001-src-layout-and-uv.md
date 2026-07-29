# 0001: src layout and uv

## Decision
Use a `src/meridian/` layout managed by `uv`, with `hatchling` as the build backend.

## Why
[write 2-4 sentences in your own words — e.g. src-layout prevents accidentally importing
the package from the repo root instead of the installed version, which catches packaging
bugs early; uv gives fast, reproducible installs via uv.lock]

## Revisit if
[e.g. if the project grows multiple packages, or if a future teammate/tool requires a
different layout]
