# ADR-0001 — Clean Architecture with the article's layer names

- **Status:** Accepted
- **Date:** 2026-08-19

## Context

This is the backend for a personal tracker agent. The website is a separate
repository, and the API is expected to grow a second entry point later (scheduled
agent runs, and possibly a queue consumer) on top of the HTTP one. The business rules
— cadences, streaks, and whatever tracking logic follows — are the part worth
protecting from churn in FastAPI, SQLAlchemy or the transport.

## Decision

Adopt Clean Architecture, using the layer names from
[“Clean Architecture with Python”](https://medium.com/@shaliamekh/clean-architecture-with-python-d62712fd8d4f):
`domain`, `ports`, `use_cases`, `adapters`, `drivers`. Add `config` for settings, which
inner layers may not import.

Dependencies point inwards only. Framework imports live in `drivers` (plus the
adapters that wrap a specific technology) and nowhere else.

Enforce it mechanically with `import-linter` contracts in `pyproject.toml`, run by
pre-commit and CI. Conventions that are not checked get violated.

## Consequences

- Adding an endpoint touches more files than a flat FastAPI app would. This is the
  price, and it is paid knowingly.
- Business rules are testable without a database, a web server or a clock, and the
  unit suite runs in milliseconds.
- A second driver (scheduler, queue consumer) reuses the use cases untouched.
- A wrong import fails CI with a message naming the two modules, so the structure
  survives contact with future contributors — human or otherwise.

## Alternatives considered

- **Router → manager → repository**, as in the previous `irl-api` project. Fewer
  files and quick to write, but the business logic ends up entangled with SQLAlchemy
  sessions and `HTTPException`s, which is exactly what makes such code hard to test
  and to move. Rejected for the core; its pragmatic touches (settings, base
  exceptions, session manager, camelCase schemas) were kept.
- **Hexagonal / ports-and-adapters only**, without a separate use-case layer.
  Nearly the same thing; the article's vocabulary was chosen because it is the
  reference this project is learning from.
