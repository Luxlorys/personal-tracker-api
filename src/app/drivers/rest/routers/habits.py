from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.drivers.rest.dependencies import (
    get_check_in_habit_use_case,
    get_create_habit_use_case,
    get_habit_use_case,
    get_list_habits_use_case,
)
from app.drivers.rest.schemas.common import ErrorResponse
from app.drivers.rest.schemas.habit import CreateCheckInRequest, CreateHabitRequest, HabitResponse
from app.use_cases.habits.check_in_habit import CheckInHabitUseCase
from app.use_cases.habits.create_habit import CreateHabitUseCase
from app.use_cases.habits.get_habit import GetHabitUseCase
from app.use_cases.habits.list_habits import ListHabitsUseCase

router = APIRouter(prefix="/habits", tags=["Habits"])

NOT_FOUND: dict[int | str, dict[str, object]] = {
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Habit not found"}
}
CONFLICT: dict[int | str, dict[str, object]] = {
    status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Cadence already met, or habit archived"}
}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_habit(
    body: CreateHabitRequest,
    use_case: Annotated[CreateHabitUseCase, Depends(get_create_habit_use_case)],
) -> HabitResponse:
    return HabitResponse.from_dto(await use_case(body.to_dto()))


@router.get("")
async def list_habits(
    use_case: Annotated[ListHabitsUseCase, Depends(get_list_habits_use_case)],
    include_archived: Annotated[bool, Query(alias="includeArchived")] = False,
) -> list[HabitResponse]:
    habits = await use_case(include_archived=include_archived)
    return [HabitResponse.from_dto(habit) for habit in habits]


@router.get("/{habit_id}", responses=NOT_FOUND)
async def get_habit(
    habit_id: UUID,
    use_case: Annotated[GetHabitUseCase, Depends(get_habit_use_case)],
) -> HabitResponse:
    return HabitResponse.from_dto(await use_case(habit_id))


@router.post("/{habit_id}/check-ins", status_code=status.HTTP_201_CREATED, responses=NOT_FOUND | CONFLICT)
async def check_in(
    habit_id: UUID,
    body: CreateCheckInRequest,
    use_case: Annotated[CheckInHabitUseCase, Depends(get_check_in_habit_use_case)],
) -> HabitResponse:
    return HabitResponse.from_dto(await use_case(body.to_dto(habit_id)))
