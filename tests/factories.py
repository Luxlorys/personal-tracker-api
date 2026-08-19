"""Builders for domain objects used across the test suite."""

from datetime import UTC, datetime, timedelta

from app.domain.entities.habit import Habit
from app.domain.value_objects.cadence import Cadence, CadencePeriod

NOW = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)


def create_habit(
    name: str = "Morning run",
    period: CadencePeriod = CadencePeriod.daily,
    target: int = 1,
    created_at: datetime | None = None,
) -> Habit:
    return Habit(
        name=name,
        cadence=Cadence(period=period, target=target),
        created_at=created_at or NOW - timedelta(days=30),
    )
