from uuid import UUID

from app.domain.entities.check_in import CheckIn
from app.domain.entities.habit import Habit
from app.ports.repositories.habit_repository import HabitRepository


class InMemoryHabitRepository(HabitRepository):
    """A real implementation of the port that happens to store nothing.

    Unit tests run the use cases against this, so they exercise the same code
    paths as production without touching PostgreSQL.
    """

    def __init__(self, habits: list[Habit] | None = None) -> None:
        self.habits: list[Habit] = habits if habits is not None else []

    async def add(self, habit: Habit) -> None:
        self.habits.append(habit)

    async def get(self, habit_id: UUID) -> Habit | None:
        return next((habit for habit in self.habits if habit.id == habit_id), None)

    async def list(self, *, include_archived: bool = False) -> list[Habit]:
        return [habit for habit in self.habits if include_archived or habit.is_active]

    async def add_check_in(self, check_in: CheckIn) -> None:
        habit = await self.get(check_in.habit_id)
        if habit is None:
            return
        if all(existing.id != check_in.id for existing in habit.check_ins):
            habit.check_ins.append(check_in)
