from datetime import timedelta
from uuid import uuid4

import pytest

from app.adapters.clock.fixed_clock import FixedClock
from app.adapters.repositories.in_memory.habit_repository import InMemoryHabitRepository
from app.domain.exceptions import CadenceAlreadyMetError
from app.domain.value_objects.cadence import CadencePeriod
from app.use_cases.dto.habit import CheckInHabitDTO, CreateHabitDTO
from app.use_cases.exceptions import FutureCheckInError, HabitNotFoundError
from app.use_cases.habits.check_in_habit import CheckInHabitUseCase
from app.use_cases.habits.create_habit import CreateHabitUseCase
from app.use_cases.habits.get_habit import GetHabitUseCase
from app.use_cases.habits.list_habits import ListHabitsUseCase
from tests.factories import NOW, create_habit


@pytest.fixture
def create_habit_use_case(habit_repository: InMemoryHabitRepository, clock: FixedClock) -> CreateHabitUseCase:
    return CreateHabitUseCase(habit_repository, clock)


@pytest.fixture
def list_habits_use_case(habit_repository: InMemoryHabitRepository, clock: FixedClock) -> ListHabitsUseCase:
    return ListHabitsUseCase(habit_repository, clock)


@pytest.fixture
def get_habit_use_case(habit_repository: InMemoryHabitRepository, clock: FixedClock) -> GetHabitUseCase:
    return GetHabitUseCase(habit_repository, clock)


@pytest.fixture
def check_in_use_case(habit_repository: InMemoryHabitRepository, clock: FixedClock) -> CheckInHabitUseCase:
    return CheckInHabitUseCase(habit_repository, clock)


async def test_create_habit_persists_and_returns_a_dto(
    create_habit_use_case: CreateHabitUseCase, habit_repository: InMemoryHabitRepository
):
    dto = await create_habit_use_case(CreateHabitDTO(name="Read", period=CadencePeriod.weekly, target=3))

    assert dto.name == "Read"
    assert dto.target == 3
    assert dto.created_at == NOW
    assert dto.current_streak == 0
    assert [habit.id for habit in habit_repository.habits] == [dto.id]


async def test_list_habits_hides_archived_by_default(
    list_habits_use_case: ListHabitsUseCase, habit_repository: InMemoryHabitRepository
):
    active = create_habit(name="Run")
    archived = create_habit(name="Old")
    archived.archive(at=NOW)
    habit_repository.habits.extend([active, archived])

    assert [dto.name for dto in await list_habits_use_case()] == ["Run"]
    assert {dto.name for dto in await list_habits_use_case(include_archived=True)} == {"Run", "Old"}


async def test_get_habit_raises_when_missing(get_habit_use_case: GetHabitUseCase):
    with pytest.raises(HabitNotFoundError):
        await get_habit_use_case(uuid4())


async def test_check_in_records_and_reports_the_streak(
    check_in_use_case: CheckInHabitUseCase, habit_repository: InMemoryHabitRepository
):
    habit = create_habit(period=CadencePeriod.daily)
    habit.check_in(at=NOW - timedelta(days=1))
    habit_repository.habits.append(habit)

    dto = await check_in_use_case(CheckInHabitDTO(habit_id=habit.id, note="done"))

    assert dto.completed_for_current_period is True
    assert dto.current_streak == 2
    assert [c.note for c in dto.check_ins if c.note] == ["done"]


async def test_check_in_defaults_to_now(
    check_in_use_case: CheckInHabitUseCase, habit_repository: InMemoryHabitRepository
):
    habit = create_habit()
    habit_repository.habits.append(habit)

    dto = await check_in_use_case(CheckInHabitDTO(habit_id=habit.id))

    assert [c.recorded_at for c in dto.check_ins] == [NOW]


async def test_check_in_in_the_future_is_rejected(
    check_in_use_case: CheckInHabitUseCase, habit_repository: InMemoryHabitRepository
):
    habit = create_habit()
    habit_repository.habits.append(habit)

    with pytest.raises(FutureCheckInError):
        await check_in_use_case(CheckInHabitDTO(habit_id=habit.id, recorded_at=NOW + timedelta(seconds=1)))


async def test_check_in_on_a_missing_habit_is_rejected(check_in_use_case: CheckInHabitUseCase):
    with pytest.raises(HabitNotFoundError):
        await check_in_use_case(CheckInHabitDTO(habit_id=uuid4()))


async def test_second_check_in_in_the_same_period_is_rejected(
    check_in_use_case: CheckInHabitUseCase, habit_repository: InMemoryHabitRepository
):
    habit = create_habit()
    habit_repository.habits.append(habit)
    await check_in_use_case(CheckInHabitDTO(habit_id=habit.id))

    with pytest.raises(CadenceAlreadyMetError):
        await check_in_use_case(CheckInHabitDTO(habit_id=habit.id))
