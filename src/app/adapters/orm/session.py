from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


class DatabaseSessionManager:
    """Owns the engine and hands out sessions. One instance per process."""

    def __init__(self, db_url: str, *, echo: bool = False, **engine_kwargs: Any) -> None:
        self._engine: AsyncEngine = create_async_engine(
            db_url,
            echo=echo,
            pool_pre_ping=True,
            pool_recycle=1800,
            **engine_kwargs,
        )
        self._session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def session(self) -> AsyncIterator[AsyncSession]:
        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def dispose(self) -> None:
        await self._engine.dispose()
