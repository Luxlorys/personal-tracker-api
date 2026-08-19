# Personal Tracker API — working agreement

Backend for a personal tracker agent. FastAPI + SQLAlchemy + PostgreSQL, structured
as Clean Architecture. The website is a separate repository; nothing frontend belongs
here.

**Read [`docs/architecture.md`](docs/architecture.md) before changing anything.** The
rules below are the short version.

## The dependency rule

Source dependencies point inwards only:

```
drivers → adapters → use_cases → ports → domain
```

| Layer (`src/app/…`) | May import | Must never import |
| ------------------- | ---------- | ----------------- |
| `domain` | the standard library only | anything |
| `ports` | `domain` | `use_cases`, `adapters`, `drivers`, frameworks |
| `use_cases` | `ports`, `domain` | `adapters`, `drivers`, frameworks, `config` |
| `adapters` | `use_cases`, `ports`, `domain`, `config` | `drivers` |
| `drivers` | everything | — |

`fastapi`, `sqlalchemy`, `pydantic`, `redis` and `alembic` must not appear in
`domain`, `ports` or `use_cases`. `uv run lint-imports` enforces this; do not add
exemptions to make a violation pass — restructure instead.

`drivers/rest/dependencies.py` is the composition root: the only place that decides
which adapter is used.

## The three model types

| Kind | Location | Built with | Never |
| ---- | -------- | ---------- | ----- |
| Request / response | `drivers/rest/schemas/` | Pydantic | reaches a use case |
| DTO | `use_cases/dto/` | frozen dataclass | carries behaviour or validation |
| ORM model | `adapters/orm/models.py` | SQLAlchemy | leaves `app.adapters` |
| *(domain entity / VO)* | `domain/` | plain dataclass | gets serialised to HTTP |

Conversions: `Request.to_dto()` · `DTO.from_entity()` · `Response.from_dto()` ·
`adapters/orm/mappers.py` for entity ↔ ORM.

## Errors

`DomainError` (domain) · `ApplicationError` (use cases) · `ExternalError` (adapters).
Library exceptions are wrapped in the adapter that caused them. Status codes exist
only in `drivers/rest/exception_handlers.py`. Error bodies are always
`{"message": "..."}`.

## Conventions

- Python 3.13, fully annotated, async throughout.
- Use cases are classes with `__init__` for dependencies and a single `__call__`.
- Use cases never call `datetime.now()` — they take the `Clock` port.
- Time is timezone-aware UTC everywhere. Never a naive datetime.
- JSON is camelCase on the wire, snake_case in Python (`CamelModel` handles it).
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `chore:`…).

## Adding a feature

Inside out: domain → port (if needed) → DTOs → use case → adapter (+ migration) →
router + schemas + wiring. `habits` is the reference slice; copy its shape.

## Before saying you are done

```bash
make lint && make test
```

`make lint` = Ruff check, Ruff format check, ty, and the architecture contracts.
Integration tests skip themselves when PostgreSQL is not running; start it with
`docker compose up -d postgres redis` if you need them.

Schema change? `make migration m="..."` and commit the generated file — CI runs
`alembic check` and fails if the models and the migrations disagree.
