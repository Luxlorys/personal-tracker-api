from app.domain.entities.habit import Habit
from app.domain.value_objects.cadence import Cadence
from app.ports.clock import Clock
from app.ports.repositories.habit_repository import HabitRepository
from app.use_cases.dto.habit import CreateHabitDTO, HabitDTO


class CreateHabitUseCase:
    def __init__(self, habit_repository: HabitRepository, clock: Clock) -> None:
        self._habit_repository = habit_repository
        self._clock = clock

    async def __call__(self, data: CreateHabitDTO) -> HabitDTO:
        now = self._clock.now()
        habit = Habit(
            name=data.name,
            cadence=Cadence(period=data.period, target=data.target),
            created_at=now,
        )
        await self._habit_repository.add(habit)
        return HabitDTO.from_entity(habit, as_of=now)
