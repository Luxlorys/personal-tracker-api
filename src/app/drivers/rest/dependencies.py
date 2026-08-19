"""The composition root: the only place that knows which adapter is used.

Every arrow in the architecture diagram is wired here. Swapping PostgreSQL for
something else means editing this file and adding an adapter — no use case, port
or entity changes.
"""

from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.clock.system_clock import SystemClock
from app.adapters.orm.session import DatabaseSessionManager
from app.adapters.repositories.sqlalchemy.habit_repository import SqlAlchemyHabitRepository
from app.config.settings import Settings, get_settings
from app.ports.clock import Clock
from app.ports.repositories.habit_repository import HabitRepository
from app.use_cases.habits.check_in_habit import CheckInHabitUseCase
from app.use_cases.habits.create_habit import CreateHabitUseCase
from app.use_cases.habits.get_habit import GetHabitUseCase
from app.use_cases.habits.list_habits import ListHabitsUseCase

SettingsDependency = Annotated[Settings, Depends(get_settings)]


def get_session_manager(request: Request) -> DatabaseSessionManager:
    return request.app.state.session_manager  # type: ignore[no-any-return]


async def get_session(
    session_manager: Annotated[DatabaseSessionManager, Depends(get_session_manager)],
) -> AsyncIterator[AsyncSession]:
    async for session in session_manager.session():
        yield session


def get_redis(request: Request) -> Redis:
    return request.app.state.redis  # type: ignore[no-any-return]


@lru_cache
def get_clock() -> Clock:
    return SystemClock()


def get_habit_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> HabitRepository:
    return SqlAlchemyHabitRepository(session)


SessionDependency = Annotated[AsyncSession, Depends(get_session)]
RedisDependency = Annotated[Redis, Depends(get_redis)]
ClockDependency = Annotated[Clock, Depends(get_clock)]
HabitRepositoryDependency = Annotated[HabitRepository, Depends(get_habit_repository)]


def get_create_habit_use_case(
    habit_repository: HabitRepositoryDependency,
    clock: ClockDependency,
) -> CreateHabitUseCase:
    return CreateHabitUseCase(habit_repository, clock)


def get_list_habits_use_case(
    habit_repository: HabitRepositoryDependency,
    clock: ClockDependency,
) -> ListHabitsUseCase:
    return ListHabitsUseCase(habit_repository, clock)


def get_habit_use_case(
    habit_repository: HabitRepositoryDependency,
    clock: ClockDependency,
) -> GetHabitUseCase:
    return GetHabitUseCase(habit_repository, clock)


def get_check_in_habit_use_case(
    habit_repository: HabitRepositoryDependency,
    clock: ClockDependency,
) -> CheckInHabitUseCase:
    return CheckInHabitUseCase(habit_repository, clock)
