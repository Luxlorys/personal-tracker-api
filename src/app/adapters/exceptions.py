"""Errors raised when an external system an adapter talks to misbehaves.

Adapters never let a driver-specific or library-specific exception escape: they
wrap it, so use cases and drivers depend on this small vocabulary instead of on
`sqlalchemy.exc` or `redis.exceptions`.
"""


class ExternalError(Exception):
    """Base class for failures of a system outside this application."""


class DatabaseError(ExternalError):
    def __init__(self, error: Exception) -> None:
        self.error = error

    def __str__(self) -> str:
        return str(self.error)


class CacheError(ExternalError):
    def __init__(self, error: Exception) -> None:
        self.error = error

    def __str__(self) -> str:
        return str(self.error)
