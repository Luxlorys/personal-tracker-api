from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repositories.sqlalchemy.habit_repository import SqlAlchemyHabitRepository
from app.domain.value_objects.cadence import CadencePeriod
from tests.factories import NOW, create_habit


@pytest.fixture
def repository(session: AsyncSession) -> SqlAlchemyHabitRepository:
    return SqlAlchemyHabitRepository(session)


async def test_add_then_get_round_trips_the_entity(repository: SqlAlchemyHabitRepository):
    habit = create_habit(name="Read", period=CadencePeriod.weekly, target=3)
    habit.check_in(at=NOW - timedelta(days=1), note="chapter 1")

    await repository.add(habit)
    stored = await repository.get(habit.id)

    assert stored == habit


async def test_get_returns_none_when_missing(repository: SqlAlchemyHabitRepository):
    assert await repository.get(uuid4()) is None


async def test_list_excludes_archived_by_default(repository: SqlAlchemyHabitRepository):
    active = create_habit(name="Run")
    archived = create_habit(name="Old")
    archived.archive(at=NOW)
    await repository.add(active)
    await repository.add(archived)

    assert [habit.name for habit in await repository.list()] == ["Run"]
    assert {habit.name for habit in await repository.list(include_archived=True)} == {"Run", "Old"}


async def test_add_check_in_is_visible_on_the_next_read(repository: SqlAlchemyHabitRepository):
    habit = create_habit()
    await repository.add(habit)

    check_in = habit.check_in(at=NOW)
    await repository.add_check_in(check_in)

    stored = await repository.get(habit.id)
    assert stored is not None
    assert [c.id for c in stored.check_ins] == [check_in.id]
