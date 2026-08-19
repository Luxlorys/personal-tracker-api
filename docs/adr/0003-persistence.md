# ADR-0003 — SQLAlchemy + PostgreSQL behind a repository port

- **Status:** Accepted
- **Date:** 2026-08-19

## Context

The tracker stores habits, check-ins and — later — agent runs and notes. The data is
relational and will be queried by time ranges and aggregates. Use cases must not know
which database is behind them.

## Decision

- **PostgreSQL 17** as the database, **SQLAlchemy 2 (async, asyncpg)** as the ORM,
  **Alembic** for migrations.
- Persistence sits behind `ports.repositories.HabitRepository`. Use cases depend on
  the ABC; `SqlAlchemyHabitRepository` and `InMemoryHabitRepository` implement it.
- ORM models are mapped to and from entities in `adapters/orm/mappers.py`.
- SQLAlchemy exceptions are wrapped in `adapters.exceptions.DatabaseError` and never
  escape the adapter.
- `DatabaseSessionManager` owns the engine; FastAPI hands out one session per request.

## Consequences

- Two representations of the same data (entity and ORM model) and a mapper between
  them, as decided in [ADR-0002](0002-three-model-types.md).
- Unit tests run against the in-memory implementation of the same port, with no
  database at all.
- Migrations are generated from the models: `make migration m="..."`. CI runs
  `alembic check` so a model change without a migration fails the build.

## Deferred: the unit of work

Each repository method commits on its own. That is correct while every use case
touches a single aggregate, and it keeps the code readable. The moment one use case
has to commit changes to two repositories atomically, introduce a `UnitOfWork` port
rather than passing `AsyncSession` into the use cases — a session in a use case
signature would put SQLAlchemy in the application layer and break contract #2.
