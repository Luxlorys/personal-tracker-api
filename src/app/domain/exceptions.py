"""Errors raised when a business rule of the domain is violated.

These belong to the innermost layer: they know nothing about HTTP, databases or
frameworks. Outer layers translate them (see `app.drivers.rest.exception_handlers`).
"""

from uuid import UUID


class DomainError(Exception):
    """Base class for every violation of a domain rule."""


class InvalidHabitNameError(DomainError):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return "Habit name must be between 1 and 120 characters"


class InvalidNoteError(DomainError):
    def __init__(self, length: int) -> None:
        self.length = length

    def __str__(self) -> str:
        return f"A check-in note may not exceed 500 characters, got {self.length}"


class InvalidCadenceTargetError(DomainError):
    def __init__(self, target: int) -> None:
        self.target = target

    def __str__(self) -> str:
        return f"Cadence target must be at least 1, got {self.target}"


class HabitArchivedError(DomainError):
    def __init__(self, habit_id: UUID) -> None:
        self.habit_id = habit_id

    def __str__(self) -> str:
        return f"Habit is archived: {self.habit_id}"


class CadenceAlreadyMetError(DomainError):
    def __init__(self, habit_id: UUID, target: int) -> None:
        self.habit_id = habit_id
        self.target = target

    def __str__(self) -> str:
        return f"Habit {self.habit_id} already reached its target of {self.target} check-in(s) for this period"
