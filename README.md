# Personal Tracker API

The backend for a personal tracker agent, built with
[FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/),
[Pydantic](https://docs.pydantic.dev/) and PostgreSQL, laid out according to
**Clean Architecture**.

The website is a separate repository. This one exposes the HTTP API only.

> **Read [`docs/architecture.md`](docs/architecture.md) before writing code.**
> It defines the layers, the dependency rule and the three model types. The rules
> there are enforced automatically by `import-linter` in CI, not just by convention.

## Stack

| Concern            | Choice                                                     |
| ------------------ | ---------------------------------------------------------- |
| Package manager    | [uv](https://docs.astral.sh/uv/)                            |
| Lint + format      | [Ruff](https://docs.astral.sh/ruff/)                        |
| Type checker       | [ty](https://docs.astral.sh/ty/) *(preview)*                |
| Web framework      | FastAPI                                                     |
| ORM / migrations   | SQLAlchemy 2 (async) + Alembic                              |
| Validation         | Pydantic v2 / pydantic-settings                             |
| Database           | PostgreSQL 17                                               |
| Cache              | Redis 8                                                     |
| Tests              | pytest + pytest-asyncio + httpx                             |
| Architecture rules | [import-linter](https://import-linter.readthedocs.io/)      |

## Quick start (Docker)

```bash
cp .env.example .env && docker compose up --build
```

- API: <http://localhost:8000>
- OpenAPI docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

Migrations run automatically on container start.

## Local development

```bash
uv sync
```

Then, with PostgreSQL and Redis running (`docker compose up -d postgres redis`):

```bash
uv run alembic upgrade head
uv run fastapi dev src/app/drivers/rest/main.py
```

## Everyday commands

```bash
make help
```

| Command             | What it does                                                       |
| ------------------- | ------------------------------------------------------------------ |
| `make install`      | `uv sync` + install the pre-commit hooks                            |
| `make lint`         | Ruff check + format check, ty, and the architecture contracts       |
| `make format`       | Ruff autofix + format                                               |
| `make test`         | The whole suite                                                     |
| `make test-unit`    | Unit tests only — no database needed                                |
| `make migration m="add x"` | Autogenerate an Alembic revision                             |
| `make upgrade`      | Apply migrations                                                    |
| `make up` / `down`  | Start / stop the Docker stack                                       |

## Adding a feature

The `habits` slice is the reference implementation. To add one, work outwards:

1. `src/app/domain/` — entity and value objects, with their invariants.
2. `src/app/ports/` — the interface the use case needs (if a new one is needed).
3. `src/app/use_cases/dto/` — the DTOs in and out.
4. `src/app/use_cases/<feature>/` — one class per use case, one `__call__`.
5. `src/app/adapters/` — ORM model, mapper, repository implementation.
6. `src/app/drivers/rest/` — request/response models, router, wiring in `dependencies.py`.
7. Tests: unit against the in-memory adapter, integration against PostgreSQL and the ASGI app.

Run `make lint` — if you got a layer wrong, the architecture contracts will say so.

## Layout

```
src/app/
├── domain/      entities + value objects        (no dependencies at all)
├── ports/       abstract interfaces             (depends on: domain)
├── use_cases/   application logic + DTOs        (depends on: ports, domain)
├── adapters/    PostgreSQL, Redis, clock, ORM   (depends on: use_cases, ports, domain)
├── drivers/     FastAPI: routers, schemas, DI   (depends on: everything)
└── config/      settings                        (only adapters + drivers may import it)
```

## Notes

- **ty is in preview.** It is wired into `make lint`, pre-commit and CI. If it ever
  blocks you, `make lint` still runs Ruff and the architecture contracts; see
  [ADR-0004](docs/adr/0004-tooling.md).
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/).
