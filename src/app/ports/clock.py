from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """Reading the current time is an external concern, so it is a port.

    Use cases never call `datetime.now()` directly; they ask a `Clock`. Tests
    inject a fixed one and get deterministic behaviour for free.
    """

    @abstractmethod
    def now(self) -> datetime:
        """Return the current moment as a timezone-aware UTC datetime."""
