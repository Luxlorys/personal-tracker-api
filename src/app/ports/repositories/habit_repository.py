from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.check_in import CheckIn
from app.domain.entities.habit import Habit


class HabitRepository(ABC):
    """The contract use cases rely on to persist habits.

    Defined here — inside the application core — so that the core owns the
    interface and the storage technology depends on it, not the other way round.
    """

    @abstractmethod
    async def add(self, habit: Habit) -> None: ...

    @abstractmethod
    async def get(self, habit_id: UUID) -> Habit | None: ...

    @abstractmethod
    async def list(self, *, include_archived: bool = False) -> list[Habit]: ...

    @abstractmethod
    async def add_check_in(self, check_in: CheckIn) -> None: ...
