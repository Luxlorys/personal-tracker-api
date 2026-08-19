from uuid import UUID

from app.ports.clock import Clock
from app.ports.repositories.habit_repository import HabitRepository
from app.use_cases.dto.habit import HabitDTO
from app.use_cases.exceptions import HabitNotFoundError


class GetHabitUseCase:
    def __init__(self, habit_repository: HabitRepository, clock: Clock) -> None:
        self._habit_repository = habit_repository
        self._clock = clock

    async def __call__(self, habit_id: UUID) -> HabitDTO:
        habit = await self._habit_repository.get(habit_id)
        if habit is None:
            raise HabitNotFoundError(habit_id)
        return HabitDTO.from_entity(habit, as_of=self._clock.now())
