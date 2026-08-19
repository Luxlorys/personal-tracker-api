import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.adapters.orm.base import Base

TEST_DB_URL = os.getenv("TEST_DB_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/tracker_test")


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    """Build a session-wide engine with the schema created from the ORM metadata.

    Skips the whole module when PostgreSQL is unreachable, so `pytest` still
    works on a machine with nothing running. CI always has the service up.
    """
    engine = create_async_engine(TEST_DB_URL)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    except (OSError, SQLAlchemyError) as e:  # pragma: no cover - depends on the developer's machine
        await engine.dispose()
        pytest.skip(f"PostgreSQL is not reachable at {TEST_DB_URL}: {e}", allow_module_level=True)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Yield a session that leaves the database empty for the next test."""
    maker = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with maker() as session:
        yield session
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
