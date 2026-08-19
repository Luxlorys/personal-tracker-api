"""DTOs: the data contract between the use cases and whatever drives them.

Plain frozen dataclasses on purpose — no Pydantic, no ORM, no framework. A DTO
carries data across a layer boundary and nothing else: no behaviour, no
invariants (those live on the entities), no serialisation concerns (those live
on the request/response models in the drivers layer).
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities.check_in import CheckIn
from app.domain.entities.habit import Habit
from app.domain.value_objects.cadence import CadencePeriod


@dataclass(frozen=True, slots=True)
class CreateHabitDTO:
    """Input of `CreateHabitUseCase`."""

    name: str
    period: CadencePeriod
    target: int


@dataclass(frozen=True, slots=True)
class CheckInHabitDTO:
    """Input of `CheckInHabitUseCase`. `recorded_at=None` means "now"."""

    habit_id: UUID
    recorded_at: datetime | None = None
    note: str | None = None


@dataclass(frozen=True, slots=True)
class CheckInDTO:
    """Output projection of a `CheckIn` entity."""

    id: UUID
    recorded_at: datetime
    note: str | None

    @classmethod
    def from_entity(cls, check_in: CheckIn) -> "CheckInDTO":
        return cls(id=check_in.id, recorded_at=check_in.recorded_at, note=check_in.note)


@dataclass(frozen=True, slots=True)
class HabitDTO:
    """Output projection of a `Habit` entity, with its derived values resolved.

    `current_streak` and `completed_for_current_period` are computed by the
    entity; flattening them here means the drivers layer never has to ask the
    domain anything.
    """

    id: UUID
    name: str
    period: CadencePeriod
    target: int
    created_at: datetime
    archived_at: datetime | None
    current_streak: int
    completed_for_current_period: bool
    check_ins: tuple[CheckInDTO, ...]

    @classmethod
    def from_entity(cls, habit: Habit, as_of: datetime) -> "HabitDTO":
        return cls(
            id=habit.id,
            name=habit.name,
            period=habit.cadence.period,
            target=habit.cadence.target,
            created_at=habit.created_at,
            archived_at=habit.archived_at,
            current_streak=habit.current_streak(as_of),
            completed_for_current_period=habit.is_completed_for(as_of),
            check_ins=tuple(CheckInDTO.from_entity(c) for c in habit.check_ins),
        )
