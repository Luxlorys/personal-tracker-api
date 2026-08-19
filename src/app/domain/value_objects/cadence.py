from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from app.domain.exceptions import InvalidCadenceTargetError

MAX_CADENCE_TARGET = 100


class CadencePeriod(StrEnum):
    daily = "daily"
    weekly = "weekly"


@dataclass(frozen=True, slots=True)
class Cadence:
    """How often a habit is meant to be performed, e.g. "3 times per week"."""

    period: CadencePeriod
    target: int = 1

    def __post_init__(self) -> None:
        if not 1 <= self.target <= MAX_CADENCE_TARGET:
            raise InvalidCadenceTargetError(self.target)

    @property
    def length(self) -> timedelta:
        return timedelta(days=1) if self.period is CadencePeriod.daily else timedelta(weeks=1)

    def period_key(self, moment: datetime) -> tuple[int, ...]:
        """Identify the cadence period a moment falls into.

        Two moments belong to the same period exactly when their keys are equal.
        """
        moment = moment.astimezone(UTC)
        if self.period is CadencePeriod.daily:
            return (moment.year, moment.month, moment.day)
        iso = moment.isocalendar()
        return (iso.year, iso.week)
