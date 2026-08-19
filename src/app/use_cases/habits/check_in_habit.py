from app.ports.clock import Clock
from app.ports.repositories.habit_repository import HabitRepository
from app.use_cases.dto.habit import CheckInHabitDTO, HabitDTO
from app.use_cases.exceptions import FutureCheckInError, HabitNotFoundError


class CheckInHabitUseCase:
    def __init__(self, habit_repository: HabitRepository, clock: Clock) -> None:
        self._habit_repository = habit_repository
        self._clock = clock

    async def __call__(self, data: CheckInHabitDTO) -> HabitDTO:
        now = self._clock.now()
        recorded_at = data.recorded_at or now
        if recorded_at > now:
            raise FutureCheckInError(recorded_at)

        habit = await self._habit_repository.get(data.habit_id)
        if habit is None:
            raise HabitNotFoundError(data.habit_id)

        # The entity enforces the cadence and the archived rule.
        check_in = habit.check_in(at=recorded_at, note=data.note)
        await self._habit_repository.add_check_in(check_in)
        return HabitDTO.from_entity(habit, as_of=now)
