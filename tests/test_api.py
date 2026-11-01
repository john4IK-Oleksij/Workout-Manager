import uuid
from collections.abc import Callable
from decimal import Decimal
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import engine

# ---------------------------------------------------------------- CRUD


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_user_and_duplicate_email(client: TestClient, make_user: Callable[..., int]):
    email = f"dup_{uuid.uuid4().hex}@example.com"
    first = client.post("/users", json={"name": "A", "email": email})
    assert first.status_code == 201
    try:
        second = client.post("/users", json={"name": "B", "email": email})
        assert second.status_code == 409
        assert "SELECT" not in second.text.upper()
    finally:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM users WHERE email = :e"), {"e": email})


def test_user_validation(client: TestClient):
    assert client.post("/users", json={"name": "X", "email": "bad"}).status_code == 422
    assert (
        client.post(
            "/users", json={"name": "X", "email": "x@example.com", "id": 5}
        ).status_code
        == 422
    )


def test_create_workout_and_validation(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    owner = make_user()
    gym = add_workout(owner, kind="gym", duration_min=60, distance_km=0)
    assert Decimal(gym["distance_km"]) == Decimal("0.00")

    payload: dict[str, Any] = {
    "owner_id": owner,
    "title": "T",
    "kind": "run",
    "duration_min": 10,
    "distance_km": 1,
    "done_on": "2026-01-10",
}
    assert client.post("/workouts", json={**payload, "kind": "boxing"}).status_code == 422
    assert client.post("/workouts", json={**payload, "duration_min": 0}).status_code == 422
    assert client.post("/workouts", json={**payload, "extra": 1}).status_code == 422
    assert client.post("/workouts", json={**payload, "owner_id": 999999}).status_code == 404


def test_list_workouts_filter_and_pagination(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    owner = make_user()
    other = make_user()
    ids = [add_workout(owner, done_on=f"2026-01-{d:02d}")["id"] for d in (1, 2, 3, 4, 5)]
    add_workout(other)

    response = client.get(f"/workouts?owner_id={owner}&limit=100")
    assert [w["id"] for w in response.json()] == ids

    page = client.get(f"/workouts?owner_id={owner}&limit=2&offset=2")
    assert [w["id"] for w in page.json()] == ids[2:4]

    assert client.get("/workouts?owner_id=999999").json() == []
    assert client.get("/workouts?limit=101").status_code == 422
    assert client.get("/workouts?limit=0").status_code == 422
    assert client.get("/workouts?offset=-1").status_code == 422


# ---------------------------------------------------------- statistics


def test_summary_values_and_empty(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    owner = make_user()
    add_workout(owner, "run", 45, "6.50", "2026-01-10")
    add_workout(owner, "gym", 75, "0", "2026-01-11")
    add_workout(make_user(), "run", 500, "99.00")

    data = client.get(f"/stats/summary?owner_id={owner}").json()
    assert data["total_workouts"] == 2
    assert data["total_minutes"] == 120
    assert Decimal(data["total_km"]) == Decimal("6.50")
    assert Decimal(data["avg_duration"]) == Decimal(60)
    assert Decimal(data["min_distance"]) == Decimal(0)
    assert Decimal(data["max_distance"]) == Decimal("6.50")

    empty = client.get(f"/stats/summary?owner_id={make_user()}").json()
    assert empty["total_workouts"] == 0
    assert empty["total_minutes"] == 0
    assert Decimal(empty["total_km"]) == 0
    assert empty["avg_duration"] is None
    assert empty["min_distance"] is None
    assert empty["max_distance"] is None

    assert client.get("/stats/summary?owner_id=0").status_code == 422


def test_by_kind(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    owner = make_user()
    add_workout(owner, "run", 30, "5.00")
    add_workout(owner, "run", 40, "7.25")
    add_workout(owner, "gym", 60, "0")

    data = client.get(f"/stats/by-kind?owner_id={owner}").json()
    assert [r["kind"] for r in data] == ["gym", "run"]
    run = data[1]
    assert run["workout_count"] == 2
    assert run["total_minutes"] == 70
    assert Decimal(run["total_km"]) == Decimal("12.25")
    assert client.get(f"/stats/by-kind?owner_id={make_user()}").json() == []


def test_by_month(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    owner = make_user()
    add_workout(owner, done_on="2026-01-05", distance_km="3.00")
    add_workout(owner, done_on="2026-01-20", distance_km="4.50")
    add_workout(owner, done_on="2026-03-01", distance_km="1.00")
    add_workout(make_user(), done_on="2026-01-05", distance_km="50.00")

    data = client.get(f"/stats/by-month?owner_id={owner}").json()
    assert [(r["month"], r["workouts_count"], Decimal(r["total_distance_km"])) for r in data] == [
        ("2026-01", 2, Decimal("7.50")),
        ("2026-03", 1, Decimal("1.00")),
    ]
    assert client.get(f"/stats/by-month?owner_id={make_user()}").json() == []


def test_top_users(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    big = make_user("Big")
    mid = make_user("Mid")
    small = make_user("Small")
    for _ in range(5):
        add_workout(big)
    for _ in range(3):
        add_workout(mid)
    add_workout(small)

    data = client.get("/stats/top-users?min_workouts=3").json()
    ids = [u["user_id"] for u in data]
    assert big in ids and mid in ids and small not in ids
    assert ids.index(big) < ids.index(mid)
    counts = [u["workouts_count"] for u in data]
    assert counts == sorted(counts, reverse=True)
    assert all(c >= 3 for c in counts)

    # exactly min_workouts is included
    exact = [u["user_id"] for u in client.get("/stats/top-users?min_workouts=5").json()]
    assert big in exact and mid not in exact

    assert client.get("/stats/top-users?min_workouts=100000").json() == []
    assert client.get("/stats/top-users?min_workouts=0").status_code == 422


def test_done_ratio(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    owner = make_user()
    add_workout(owner, duration_min=59)
    add_workout(owner, duration_min=60)
    add_workout(owner, duration_min=90)

    data = client.get(f"/stats/done-ratio?owner_id={owner}").json()
    assert data == {"owner_id": owner, "long_workouts_count": 2, "total_workouts_count": 3}

    empty = client.get(f"/stats/done-ratio?owner_id={make_user()}").json()
    assert empty["long_workouts_count"] == 0 and empty["total_workouts_count"] == 0
    assert client.get("/stats/done-ratio?owner_id=999999").status_code == 404


# ------------------------------------------------- dynamic aggregation


def test_group_valid_combinations(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    owner = make_user()
    add_workout(owner, "run", 30, "5.00")
    add_workout(owner, "run", 50, "3.00")
    add_workout(owner, "gym", 60, "0")
    add_workout(make_user(), "run", 999, "99.00")

    def group(group_by: str, metric: str) -> dict[str, Any]:
        response = client.get(
                f"/stats/group?group_by={group_by}&metric={metric}&owner_id={owner}"
            )   
        assert response.status_code == 200

        return {
        row["group_value"]: row["value"]
        for row in response.json()
    }

    assert group("kind", "count") == {"gym": 1, "run": 2}
    assert group("kind", "sum_duration") == {"gym": 60, "run": 80}
    distance = group("kind", "sum_distance")
    assert Decimal(distance["run"]) == Decimal("8.00")
    avg = group("kind", "avg_duration")
    assert Decimal(avg["run"]) == Decimal(40)
    assert group("owner_id", "count") == {owner: 3}


def test_group_invalid_params_return_422(client: TestClient):
    bad = [
        "group_by=unknown_field&metric=count&owner_id=1",
        "group_by=kind&metric=delete&owner_id=1",
        "group_by=kind&metric=count);DROP%20TABLE%20users;--&owner_id=1",
        "group_by=&metric=count&owner_id=1",
        "group_by=kind&metric=&owner_id=1",
        "group_by=kind&metric=count",
    ]
    for query in bad:
        response = client.get(f"/stats/group?{query}")
        assert response.status_code == 422, query
        assert "SELECT" not in response.text.upper()


# ---------------------------------------------------- window functions


def test_running_total(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    owner = make_user()
    add_workout(owner, distance_km="5.00", done_on="2026-01-12")
    add_workout(owner, distance_km="3.50", done_on="2026-01-10")
    add_workout(owner, distance_km="2.00", done_on="2026-01-10")
    add_workout(make_user(), distance_km="40.00", done_on="2026-01-11")

    data = client.get(f"/stats/running-total?owner_id={owner}").json()
    assert [r["done_on"] for r in data] == ["2026-01-10", "2026-01-10", "2026-01-12"]
    assert [Decimal(r["running_total_km"]) for r in data] == [
        Decimal("3.50"),
        Decimal("5.50"),
        Decimal("10.50"),
    ]
    assert client.get(f"/stats/running-total?owner_id={make_user()}").json() == []


def test_rank_with_ties(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    owner = make_user()
    add_workout(owner, "run", 60)
    add_workout(owner, "gym", 60)
    add_workout(owner, "yoga", 30)
    add_workout(owner, "swim", 100)

    data = client.get(f"/stats/rank?owner_id={owner}").json()
    assert [(r["kind"], r["total_duration_min"], r["rank"]) for r in data] == [
        ("swim", 100, 1),
        ("gym", 60, 2),
        ("run", 60, 2),
        ("yoga", 30, 4),
    ]
    assert client.get(f"/stats/rank?owner_id={make_user()}").json() == []
    assert client.get("/stats/rank?owner_id=0").status_code == 422


# ------------------------------------------------------------ security


def test_engine_hides_parameters():
    assert engine.hide_parameters is True


def test_owner_isolation_in_all_owner_endpoints(client: TestClient, make_user: Callable[..., int], add_workout: Callable[..., dict[str, Any]]):
    owner = make_user()
    stranger = make_user()
    add_workout(stranger, distance_km="9.00")
    for path in ("by-kind", "by-month", "running-total", "rank"):
        assert client.get(f"/stats/{path}?owner_id={owner}").json() == [], path

