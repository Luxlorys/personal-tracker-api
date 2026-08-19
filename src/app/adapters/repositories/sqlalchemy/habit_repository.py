from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.exceptions import DatabaseError
from app.adapters.orm.mappers import check_in_to_model, habit_to_entity, habit_to_model
from app.adapters.orm.models import HabitModel
from app.domain.entities.check_in import CheckIn
from app.domain.entities.habit import Habit
from app.ports.repositories.habit_repository import HabitRepository


class SqlAlchemyHabitRepository(HabitRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, habit: Habit) -> None:
        try:
            self._session.add(habit_to_model(habit))
            await self._session.commit()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise DatabaseError(e) from e

    async def get(self, habit_id: UUID) -> Habit | None:
        try:
            result = await self._session.execute(select(HabitModel).where(HabitModel.id == habit_id))
            model = result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(e) from e
        return habit_to_entity(model) if model else None

    async def list(self, *, include_archived: bool = False) -> list[Habit]:
        query = select(HabitModel).order_by(HabitModel.created_at)
        if not include_archived:
            query = query.where(HabitModel.archived_at.is_(None))
        try:
            result = await self._session.execute(query)
            models = result.scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError(e) from e
        return [habit_to_entity(model) for model in models]

    async def add_check_in(self, check_in: CheckIn) -> None:
        try:
            self._session.add(check_in_to_model(check_in))
            await self._session.commit()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise DatabaseError(e) from e
