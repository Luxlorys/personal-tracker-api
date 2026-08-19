# ADR-0002 — Three model types, kept separate

- **Status:** Accepted
- **Date:** 2026-08-19

## Context

Data crosses three boundaries: the network, the layer boundaries inside the process,
and the database. A single class serving all three (the “one Pydantic model
everywhere” pattern, or ORM models returned straight from routers) ties them
together: a column rename breaks the public API, an API field forces a migration, and
nothing can be tested without a database.

## Decision

Three model types, one per boundary, plus the domain objects — which are not models.

1. **Request / response models** — Pydantic, in `drivers/rest/schemas/`. The public
   HTTP contract and the OpenAPI schema. Structural validation only.
2. **DTOs** — frozen dataclasses, in `use_cases/dto/`. The input and output types of
   use cases. Plain data: no behaviour, no validation, no framework imports.
3. **ORM models** — SQLAlchemy, in `adapters/orm/models.py`. The shape of a row.
   Never leave the adapters layer.

Alongside them, **domain entities and value objects** (plain dataclasses in `domain/`)
hold the business rules and their invariants. They are constructed and manipulated by
use cases and never serialised directly.

Conversions are owned by the side that may see both types:

| Conversion | Owned by |
| ---------- | -------- |
| request model → DTO | `CreateHabitRequest.to_dto()` |
| entity → DTO | `HabitDTO.from_entity()` |
| DTO → response model | `HabitResponse.from_dto()` |
| entity ↔ ORM model | `adapters/orm/mappers.py` |

## Consequences

- Roughly two extra mapping hops per request, and a mapper to update when a field is
  added. Accepted: the mapping is trivial, explicit, and fails loudly.
- The public API can stay stable across schema changes, and vice versa.
- Use cases and the domain are importable and testable with no database and no
  FastAPI, which is what makes the unit suite fast.
- `HabitDTO` flattens derived values (`current_streak`,
  `completed_for_current_period`) so the drivers layer never has to ask the domain a
  question.

## Alternatives considered

- **Entity doubles as the DTO** (what the reference repository does): three model
  types total and half the mapping. Rejected because entities would then leak to the
  drivers layer, and every field they gain would become part of the HTTP surface by
  accident.
- **Pydantic for DTOs.** Rejected: it puts a framework in the application layer and
  invites validation to drift inwards, where the entity should own it.
