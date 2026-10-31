from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import User, Workout
from app.schemas import (
    DoneRatioResponse,
    MonthlyStatsResponse,
    SummaryResponse,
    TopUserStatsResponse,
    WorkoutKind,
    WorkoutKindStats,
)

LONG_WORKOUT_MIN_DURATION = 60


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



def get_stats_by_month(
    session: Session,
    owner_id: int,
) -> list[MonthlyStatsResponse]:
    """Calculate workout count and total distance per calendar month for a user."""
    month_expr = func.date_format(Workout.done_on, "%Y-%m")

    stmt = (
        select(
            month_expr.label("month"),
            func.count(Workout.id).label("workouts_count"),
            func.coalesce(
                func.sum(Workout.distance_km), Decimal("0.00")
            ).label("total_distance_km"),
        )
        .where(Workout.owner_id == owner_id)
        .group_by(month_expr)
        .order_by(month_expr)
    )

    rows = session.execute(stmt).all()

    return [
        MonthlyStatsResponse(
            month=row.month,
            workouts_count=int(row.workouts_count),
            total_distance_km=Decimal(row.total_distance_km),
        )
        for row in rows
    ]


def get_top_users(
    session: Session,
    min_workouts: int,
) -> list[TopUserStatsResponse]:
    """Return users having at least min_workouts workouts, most active first."""
    workouts_count = func.count(Workout.id)

    stmt = (
        select(
            User.id.label("user_id"),
            User.name.label("name"),
            workouts_count.label("workouts_count"),
        )
        .join(Workout, Workout.owner_id == User.id)
        .group_by(User.id, User.name)
        .having(workouts_count >= min_workouts)
        .order_by(workouts_count.desc(), User.id.asc())
    )

    rows = session.execute(stmt).all()

    return [
        TopUserStatsResponse(
            user_id=row.user_id,
            name=row.name,
            workouts_count=int(row.workouts_count),
        )
        for row in rows
    ]


def get_done_ratio(session: Session, owner_id: int) -> DoneRatioResponse:
    """Count long workouts (duration >= 60 min) and all workouts of a user."""
    owner_exists = session.scalar(select(User.id).where(User.id == owner_id))
    if owner_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner user not found",
        )

    stmt = select(
        func.count(
            case((Workout.duration_min >= LONG_WORKOUT_MIN_DURATION, Workout.id))
        ).label("long_workouts_count"),
        func.count(Workout.id).label("total_workouts_count"),
    ).where(Workout.owner_id == owner_id)

    row = session.execute(stmt).one()

    return DoneRatioResponse(
        owner_id=owner_id,
        long_workouts_count=int(row.long_workouts_count),
        total_workouts_count=int(row.total_workouts_count),
    )
