"""Request/response models — the public HTTP contract, and the OpenAPI schema.

These exist to validate and document what crosses the network. They convert to
and from DTOs and never reach further inwards than that: a use case must never
receive a Pydantic model, and an entity must never be serialised directly.
"""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.domain.value_objects.cadence import CadencePeriod
from app.drivers.rest.schemas.common import CamelModel
from app.use_cases.dto.habit import CheckInDTO, CheckInHabitDTO, CreateHabitDTO, HabitDTO


class CreateHabitRequest(CamelModel):
    name: str = Field(min_length=1, max_length=120, examples=["Morning run"])
    period: CadencePeriod = Field(default=CadencePeriod.daily, examples=[CadencePeriod.weekly])
    target: int = Field(default=1, ge=1, le=100, description="How many times per period", examples=[3])

    def to_dto(self) -> CreateHabitDTO:
        return CreateHabitDTO(name=self.name, period=self.period, target=self.target)


class CreateCheckInRequest(CamelModel):
    recorded_at: datetime | None = Field(default=None, description="Defaults to now")
    note: str | None = Field(default=None, max_length=500)

    def to_dto(self, habit_id: UUID) -> CheckInHabitDTO:
        return CheckInHabitDTO(habit_id=habit_id, recorded_at=self.recorded_at, note=self.note)


class CheckInResponse(CamelModel):
    id: UUID
    recorded_at: datetime
    note: str | None

    @classmethod
    def from_dto(cls, dto: CheckInDTO) -> "CheckInResponse":
        return cls(id=dto.id, recorded_at=dto.recorded_at, note=dto.note)


class HabitResponse(CamelModel):
    id: UUID
    name: str
    period: CadencePeriod
    target: int
    created_at: datetime
    archived_at: datetime | None
    current_streak: int
    completed_for_current_period: bool
    check_ins: list[CheckInResponse]

    @classmethod
    def from_dto(cls, dto: HabitDTO) -> "HabitResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            period=dto.period,
            target=dto.target,
            created_at=dto.created_at,
            archived_at=dto.archived_at,
            current_streak=dto.current_streak,
            completed_for_current_period=dto.completed_for_current_period,
            check_ins=[CheckInResponse.from_dto(c) for c in dto.check_ins],
        )
