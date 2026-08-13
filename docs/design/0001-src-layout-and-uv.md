# 0001: src layout and uv

**Day:** 1

## Decision
Package code lives under `src/meridian/`, not a flat top-level `meridian/`. Dependency
and environment management goes through `uv`, not bare `pip`/`venv`.

## Why
The `src/` layout is a small amount of upfront annoyance that pays for itself the first
time a test accidentally imports the package sitting in the current directory instead of
the one that's actually installed. That bug is sneaky precisely because it only shows up
on someone else's machine, or in CI, never on yours — so I'd rather structure the repo so
it's not possible in the first place than debug it later.

`uv` won over `pip`/`poetry` for boring reasons: one lockfile (`uv.lock`), one tool for
both dependency resolution and the venv itself, and no "did I remember to activate it"
ritual every time I open a new shell. Nothing exotic here, just fewer moving parts.

## Revisit if
Never expect to, honestly — this is about as low-risk a foundational choice as they come.
If anything, it'd be uv's ecosystem maturity that forces a rethink, not the layout.
