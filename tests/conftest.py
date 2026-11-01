import uuid
from collections.abc import Callable, Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database import SessionLocal
from app.main import app
from app.models import User, Workout


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client running against the configured MySQL/MariaDB."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def make_user(
    client: TestClient,
) -> Generator[Callable[..., int], None, None]:
    """Create isolated users through the API and delete them after the test."""

    created_ids: list[int] = []

    def _make_user(name: str = "Test User") -> int:
        email = f"test_{uuid.uuid4().hex}@example.com"

        response = client.post(
            "/users",
            json={"name": name, "email": email},
        )

        assert response.status_code == 201, response.text

        response_data: dict[str, Any] = response.json()
        user_id = int(response_data["id"])
        created_ids.append(user_id)

        return user_id

    yield _make_user

    with SessionLocal() as session:
        if created_ids:
            session.execute(
                delete(Workout).where(Workout.owner_id.in_(created_ids))
            )
            session.execute(
                delete(User).where(User.id.in_(created_ids))
            )
            session.commit()


@pytest.fixture
def add_workout(
    client: TestClient,
) -> Callable[..., dict[str, Any]]:
    """Create a workout through the API."""

    def _add_workout(
        owner_id: int,
        kind: str = "run",
        duration_min: int = 30,
        distance_km: str | float | int = "5.00",
        done_on: str = "2026-01-10",
        title: str = "Test workout",
    ) -> dict[str, Any]:
        response = client.post(
            "/workouts",
            json={
                "owner_id": owner_id,
                "title": title,
                "kind": kind,
                "duration_min": duration_min,
                "distance_km": distance_km,
                "done_on": done_on,
            },
        )

        assert response.status_code == 201, response.text

        response_data: dict[str, Any] = response.json()
        return response_data

    return _add_workout
