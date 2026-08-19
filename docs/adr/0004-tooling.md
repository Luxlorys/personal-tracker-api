# ADR-0004 — uv, Ruff, ty, Docker Compose

- **Status:** Accepted
- **Date:** 2026-08-19

## Context

A solo project that should stay fast to work in and reproducible across a laptop, CI
and a container.

## Decision

| Concern | Tool | Notes |
| ------- | ---- | ----- |
| Packaging, venv, lockfile | **uv** | `uv.lock` is committed; CI runs `--frozen`. |
| Lint + format | **Ruff** | `select = ["ALL"]` with an explicit ignore list, so new rules arrive opted-in rather than unnoticed. |
| Types | **ty** | Astral's checker. |
| Architecture | **import-linter** | The contracts in [`docs/architecture.md`](../architecture.md). |
| Tests | **pytest** + pytest-asyncio + httpx | `asyncio_mode = "auto"`. |
| Local stack | **Docker Compose** | API + PostgreSQL 17 + Redis 8, with healthchecks. |
| Hooks | **pre-commit** + gitlint | Conventional Commits. |

The package lives at `src/app/`, installed into the venv, so imports are
`from app.domain...` everywhere with no `PYTHONPATH` juggling.

## Consequences

- One command (`make check`) reproduces CI exactly.
- Ruff with `ALL` is noisy by default; the ignore list in `pyproject.toml` is the
  project's style, and each entry is commented.

## The risk with ty

**ty is pre-1.0.** It is fast and it already catches real mistakes, but its rules and
its configuration format can still change under us. Mitigation: the version is in
`uv.lock`, so an upgrade is deliberate; and `make lint` runs Ruff and the import
contracts independently, so neither depends on ty working.

If ty ever becomes an obstacle, swapping in mypy means adding the dependency and a
`[tool.mypy]` block, and changing two lines in `Makefile` and the CI workflow. Nothing
in `src/` would change — the code is annotated either way.
