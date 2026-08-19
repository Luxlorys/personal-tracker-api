import pytest
from pytest_asyncio import is_async_test

from app.adapters.clock.fixed_clock import FixedClock
from app.adapters.repositories.in_memory.habit_repository import InMemoryHabitRepository
from tests.factories import NOW


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for test in (item for item in items if is_async_test(item)):
        test.add_marker(session_scope_marker, append=False)


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(NOW)


@pytest.fixture
def habit_repository() -> InMemoryHabitRepository:
    return InMemoryHabitRepository()
