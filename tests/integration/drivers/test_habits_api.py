"""The HTTP contract, exercised end to end with an in-memory repository.

Only the adapters are swapped: routing, schema validation, the use cases and the
domain rules all run for real.
"""

from collections.abc import AsyncIterator
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from app.adapters.clock.fixed_clock import FixedClock
from app.adapters.repositories.in_memory.habit_repository import InMemoryHabitRepository
from app.drivers.rest.dependencies import get_clock, get_habit_repository
from app.drivers.rest.main import create_app
from tests.factories import NOW


@pytest.fixture
def app(habit_repository: InMemoryHabitRepository, clock: FixedClock) -> FastAPI:
    app = create_app()
    app.dependency_overrides[get_habit_repository] = lambda: habit_repository
    app.dependency_overrides[get_clock] = lambda: clock
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


async def test_create_habit_returns_201_and_the_camel_cased_body(client: AsyncClient):
    response = await client.post("/habits", json={"name": "Read", "period": "weekly", "target": 3})

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["name"] == "Read"
    assert body["target"] == 3
    assert body["currentStreak"] == 0
    assert body["completedForCurrentPeriod"] is False


async def test_create_habit_rejects_an_invalid_payload(client: AsyncClient):
    response = await client.post("/habits", json={"name": "", "period": "yearly"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_list_habits_returns_what_was_created(client: AsyncClient):
    await client.post("/habits", json={"name": "Read"})
    response = await client.get("/habits")

    assert response.status_code == status.HTTP_200_OK
    assert [habit["name"] for habit in response.json()] == ["Read"]


async def test_get_unknown_habit_returns_404(client: AsyncClient):
    response = await client.get(f"/habits/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["message"].lower()


async def test_check_in_returns_the_updated_streak(client: AsyncClient):
    habit_id = (await client.post("/habits", json={"name": "Run"})).json()["id"]

    response = await client.post(f"/habits/{habit_id}/check-ins", json={"note": "5k"})

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["currentStreak"] == 1
    assert body["completedForCurrentPeriod"] is True
    assert body["checkIns"][0]["note"] == "5k"


async def test_second_check_in_in_the_same_period_returns_409(client: AsyncClient):
    habit_id = (await client.post("/habits", json={"name": "Run"})).json()["id"]
    await client.post(f"/habits/{habit_id}/check-ins", json={})

    response = await client.post(f"/habits/{habit_id}/check-ins", json={})

    assert response.status_code == status.HTTP_409_CONFLICT


async def test_check_in_in_the_future_returns_422(client: AsyncClient):
    habit_id = (await client.post("/habits", json={"name": "Run"})).json()["id"]
    future = (NOW + timedelta(days=1)).isoformat()

    response = await client.post(f"/habits/{habit_id}/check-ins", json={"recordedAt": future})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
