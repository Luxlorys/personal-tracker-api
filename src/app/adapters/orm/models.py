"""SQLAlchemy models — the shape of the data *in PostgreSQL*.

They are a persistence detail, not the domain. Nothing outside
`app.adapters` may import them; repositories translate them to and from domain
entities in `app.adapters.orm.mappers`.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.orm.base import Base


class HabitModel(Base):
    __tablename__ = "habits"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    cadence_period: Mapped[str] = mapped_column(String(16), nullable=False)
    cadence_target: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    check_ins: Mapped[list["CheckInModel"]] = relationship(
        back_populates="habit",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CheckInModel.recorded_at",
    )

    def __repr__(self) -> str:
        return f"<HabitModel id={self.id} name={self.name!r}>"


class CheckInModel(Base):
    __tablename__ = "habit_check_ins"
    __table_args__ = (Index("ix_habit_check_ins_habit_id_recorded_at", "habit_id", "recorded_at"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    habit_id: Mapped[UUID] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    habit: Mapped[HabitModel] = relationship(back_populates="check_ins")

    def __repr__(self) -> str:
        return f"<CheckInModel id={self.id} habit_id={self.habit_id}>"
