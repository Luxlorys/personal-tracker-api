"""Errors raised by use cases when the application cannot honour a request.

Distinct from `app.domain.exceptions`, which cover violations of business rules
that hold regardless of the application surrounding them.
"""

from datetime import datetime
from uuid import UUID


class ApplicationError(Exception):
    """Base class for every error raised by a use case."""


class HabitNotFoundError(ApplicationError):
    def __init__(self, habit_id: UUID) -> None:
        self.habit_id = habit_id

    def __str__(self) -> str:
        return f"Habit not found: {self.habit_id}"


class FutureCheckInError(ApplicationError):
    def __init__(self, recorded_at: datetime) -> None:
        self.recorded_at = recorded_at

    def __str__(self) -> str:
        return f"A check-in cannot be recorded in the future: {self.recorded_at.isoformat()}"
