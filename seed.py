from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal, init_db
from app.models import User, Workout

SEED_USERS: list[tuple[str, str]] = [
    ("Ivan Petrenko", "ivan@example.com"),
    ("Olena Kovalenko", "olena@example.com"),
    ("Andrii Shevchenko", "andrii@example.com"),
]


def build_seed_workouts(user_ids_by_email: dict[str, int]) -> list[Workout]:
    """Build deterministic workout ORM instances distributed across 3 users and 3 months."""
    ivan_id = user_ids_by_email["ivan@example.com"]
    olena_id = user_ids_by_email["olena@example.com"]
    andrii_id = user_ids_by_email["andrii@example.com"]

    return [
        # Ivan Petrenko — 7 workouts across Jan, Feb, Mar 2026
        Workout(
            owner_id=ivan_id,
            title="Morning Park Run",
            kind="run",
            duration_min=45,
            distance_km=Decimal("7.50"),
            done_on=date(2026, 1, 10),
        ),
        Workout(
            owner_id=ivan_id,
            title="Upper Body Strength",
            kind="gym",
            duration_min=60,
            distance_km=Decimal("0.00"),
            done_on=date(2026, 1, 18),
        ),
        Workout(
            owner_id=ivan_id,
            title="Endurance Pool Session",
            kind="swim",
            duration_min=50,
            distance_km=Decimal("2.00"),
            done_on=date(2026, 1, 25),
        ),
        Workout(
            owner_id=ivan_id,
            title="Tempo Road Run",
            kind="run",
            duration_min=65,
            distance_km=Decimal("11.20"),
            done_on=date(2026, 2, 7),
        ),
        Workout(
            owner_id=ivan_id,
            title="Leg Day Workout",
            kind="gym",
            duration_min=75,
            distance_km=Decimal("0.00"),
            done_on=date(2026, 2, 19),
        ),
        Workout(
            owner_id=ivan_id,
            title="Recovery Mobility Yoga",
            kind="yoga",
            duration_min=40,
            distance_km=Decimal("0.00"),
            done_on=date(2026, 3, 5),
        ),
        Workout(
            owner_id=ivan_id,
            title="Half-Marathon Prep Run",
            kind="run",
            duration_min=90,
            distance_km=Decimal("16.40"),
            done_on=date(2026, 3, 21),
        ),
        # Olena Kovalenko — 5 workouts across Jan, Feb, Mar 2026
        Workout(
            owner_id=olena_id,
            title="Sunrise Vinyasa Flow",
            kind="yoga",
            duration_min=60,
            distance_km=Decimal("0.00"),
            done_on=date(2026, 1, 12),
        ),
        Workout(
            owner_id=olena_id,
            title="Easy Evening Jog",
            kind="run",
            duration_min=35,
            distance_km=Decimal("5.00"),
            done_on=date(2026, 1, 28),
        ),
        Workout(
            owner_id=olena_id,
            title="Freestyle Swim Drills",
            kind="swim",
            duration_min=45,
            distance_km=Decimal("1.50"),
            done_on=date(2026, 2, 11),
        ),
        Workout(
            owner_id=olena_id,
            title="Deep Stretch Yoga",
            kind="yoga",
            duration_min=70,
            distance_km=Decimal("0.00"),
            done_on=date(2026, 2, 24),
        ),
        Workout(
            owner_id=olena_id,
            title="Spring 10K Run",
            kind="run",
            duration_min=58,
            distance_km=Decimal("10.00"),
            done_on=date(2026, 3, 14),
        ),
        # Andrii Shevchenko — 4 workouts across Jan, Feb, Mar 2026
        Workout(
            owner_id=andrii_id,
            title="Full Body Circuit",
            kind="gym",
            duration_min=65,
            distance_km=Decimal("0.00"),
            done_on=date(2026, 1, 15),
        ),
        Workout(
            owner_id=andrii_id,
            title="Interval Track Run",
            kind="run",
            duration_min=40,
            distance_km=Decimal("6.80"),
            done_on=date(2026, 2, 9),
        ),
        Workout(
            owner_id=andrii_id,
            title="Evening Lap Swim",
            kind="swim",
            duration_min=60,
            distance_km=Decimal("2.40"),
            done_on=date(2026, 3, 3),
        ),
        Workout(
            owner_id=andrii_id,
            title="Core & Balance Yoga",
            kind="yoga",
            duration_min=30,
            distance_km=Decimal("0.00"),
            done_on=date(2026, 3, 18),
        ),
    ]


def seed_database() -> None:
    """Populate the database with reproducible seed users and workouts."""
    init_db()
    session = SessionLocal()
    try:
        seed_emails = [email for _, email in SEED_USERS]
        existing_users = list(
            session.scalars(
                select(User).where(User.email.in_(seed_emails))
            ).all()
        )
        if existing_users:
            print(
                "Seed data already exists in the database "
                f"({len(existing_users)} seed user(s) found). Skipping seeding."
            )
            return

        users = [User(name=name, email=email) for name, email in SEED_USERS]
        session.add_all(users)
        session.flush()

        user_ids_by_email = {user.email: user.id for user in users}
        workouts = build_seed_workouts(user_ids_by_email)
        session.add_all(workouts)

        session.commit()
        print(
            f"Successfully seeded {len(users)} users and {len(workouts)} workouts."
        )
    except SQLAlchemyError:
        session.rollback()
        print("Error: Failed to seed the database due to a database error.")
        raise SystemExit(1) from None
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
