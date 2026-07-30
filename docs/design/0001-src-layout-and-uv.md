# 0001: src layout and uv

## Decision
packages code lives under `src/meridian`, not a flat top-level `meridian\`.
Dependency and environment management is `uv`, not bare `pip / venv`

## Why
A `src/` layout forces tests to import the *installed* package, not whatever happens to be
in the current directory - it catches "works on my machine because I'm sitting in the right folder"
packaging bugs early, for free. `uv` was chosen over `pip`/`poetry` for a fast, reproducible,
single-lockfile workflow (`uv.lock`) with no separate virtualenv-activation ritual to forget.
