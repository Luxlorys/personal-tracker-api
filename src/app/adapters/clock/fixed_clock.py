from datetime import datetime

from app.ports.clock import Clock


class FixedClock(Clock):
    """A clock that always reports the same moment. For tests and fixtures."""

    def __init__(self, moment: datetime) -> None:
        self._moment = moment

    def now(self) -> datetime:
        return self._moment

    def set(self, moment: datetime) -> None:
        self._moment = moment
