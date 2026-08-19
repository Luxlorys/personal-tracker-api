from app.ports.clock import Clock
from app.ports.repositories.habit_repository import HabitRepository
from app.use_cases.dto.habit import HabitDTO


class ListHabitsUseCase:
    def __init__(self, habit_repository: HabitRepository, clock: Clock) -> None:
        self._habit_repository = habit_repository
        self._clock = clock

    async def __call__(self, *, include_archived: bool = False) -> list[HabitDTO]:
        now = self._clock.now()
        habits = await self._habit_repository.list(include_archived=include_archived)
        return [HabitDTO.from_entity(habit, as_of=now) for habit in habits]
