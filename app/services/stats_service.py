from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Workout
from app.schemas import SummaryResponse, WorkoutKind, WorkoutKindStats


def get_summary(session: Session, owner_id: int) -> SummaryResponse:
    """Calculate summary workout statistics for a user in a single SQL query."""
    stmt = select(
        func.count(Workout.id).label("total_workouts"),
        func.coalesce(func.sum(Workout.duration_min), 0).label("total_minutes"),
        func.coalesce(
            func.sum(Workout.distance_km), Decimal("0.00")
        ).label("total_km"),
        func.avg(Workout.duration_min).label("avg_duration"),
        func.min(Workout.distance_km).label("min_distance"),
        func.max(Workout.distance_km).label("max_distance"),
    ).where(Workout.owner_id == owner_id)

    row = session.execute(stmt).one()

    return SummaryResponse(
        owner_id=owner_id,
        total_workouts=int(row.total_workouts),
        total_minutes=int(row.total_minutes),
        total_km=Decimal(row.total_km),
        avg_duration=row.avg_duration,
        min_distance=row.min_distance,
        max_distance=row.max_distance,
    )


def get_stats_by_kind(
    session: Session,
    owner_id: int,
) -> list[WorkoutKindStats]:
    """Calculate workout statistics grouped by workout kind for a user."""
    stmt = (
        select(
            Workout.kind,
            func.count(Workout.id).label("workout_count"),
            func.coalesce(func.sum(Workout.duration_min), 0).label(
                "total_minutes"
            ),
            func.coalesce(
                func.sum(Workout.distance_km), Decimal("0.00")
            ).label("total_km"),
        )
        .where(Workout.owner_id == owner_id)
        .group_by(Workout.kind)
        .order_by(Workout.kind)
    )

    rows = session.execute(stmt).all()

    return [
        WorkoutKindStats(
            kind=WorkoutKind(row.kind),
            workout_count=int(row.workout_count),
            total_minutes=int(row.total_minutes),
            total_km=Decimal(row.total_km),
        )
        for row in rows
    ]

