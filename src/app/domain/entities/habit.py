from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.entities.check_in import CheckIn
from app.domain.exceptions import CadenceAlreadyMetError, HabitArchivedError, InvalidHabitNameError
from app.domain.value_objects.cadence import Cadence

MAX_HABIT_NAME_LENGTH = 120


@dataclass
class Habit:
    """Something the user wants to do repeatedly, plus the record of doing it.

    This is the aggregate root: check-ins are only ever created through
    `check_in()`, so the cadence rule cannot be bypassed.
    """

    name: str
    cadence: Cadence
    created_at: datetime
    id: UUID = field(default_factory=uuid4)
    archived_at: datetime | None = None
    check_ins: list[CheckIn] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not 1 <= len(self.name) <= MAX_HABIT_NAME_LENGTH:
            raise InvalidHabitNameError(self.name)

    @property
    def is_active(self) -> bool:
        return self.archived_at is None

    def check_in(self, at: datetime, note: str | None = None) -> CheckIn:
        """Record one occurrence of the habit, enforcing the cadence."""
        if not self.is_active:
            raise HabitArchivedError(self.id)
        if self.is_completed_for(at):
            raise CadenceAlreadyMetError(self.id, self.cadence.target)

        check_in = CheckIn(habit_id=self.id, recorded_at=at, note=note)
        self.check_ins.append(check_in)
        return check_in

    def archive(self, at: datetime) -> None:
        if not self.is_active:
            raise HabitArchivedError(self.id)
        self.archived_at = at

    def completed_count_for(self, moment: datetime) -> int:
        """How many check-ins fall in the same cadence period as `moment`."""
        key = self.cadence.period_key(moment)
        return sum(1 for check_in in self.check_ins if self.cadence.period_key(check_in.recorded_at) == key)

    def is_completed_for(self, moment: datetime) -> bool:
        return self.completed_count_for(moment) >= self.cadence.target

    def current_streak(self, as_of: datetime) -> int:
        """Consecutive completed periods ending at `as_of`.

        The period `as_of` falls into is still in progress, so leaving it
        incomplete does not break the streak — it just does not extend it.
        """
        cursor = as_of
        if not self.is_completed_for(cursor):
            cursor -= self.cadence.length

        streak = 0
        while self.is_completed_for(cursor):
            streak += 1
            cursor -= self.cadence.length
        return streak
