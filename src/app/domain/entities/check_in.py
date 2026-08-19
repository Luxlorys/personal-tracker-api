from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.exceptions import InvalidNoteError

MAX_NOTE_LENGTH = 500


@dataclass
class CheckIn:
    """A single recorded occurrence of a habit."""

    habit_id: UUID
    recorded_at: datetime
    note: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.note is not None and len(self.note) > MAX_NOTE_LENGTH:
            raise InvalidNoteError(len(self.note))
