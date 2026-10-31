from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import User, Workout
from app.schemas import WorkoutCreate


def create_workout(session: Session, workout_data: WorkoutCreate) -> Workout:
    """Create and persist a new workout for an existing user."""
    owner = session.scalar(
        select(User).where(User.id == workout_data.owner_id)
    )
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner user not found",
        )

    workout = Workout(
        owner_id=workout_data.owner_id,
        title=workout_data.title,
        kind=workout_data.kind.value,
        duration_min=workout_data.duration_min,
        distance_km=workout_data.distance_km,
        done_on=workout_data.done_on,
    )
    session.add(workout)
    try:
        session.commit()
        session.refresh(workout)
        return workout
    except SQLAlchemyError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workout",
        ) from None


def get_workouts(
    session: Session,
    owner_id: int | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Workout]:
    """Retrieve a paginated list of workouts, optionally filtered by owner_id."""
    stmt = select(Workout)

    if owner_id is not None:
        stmt = stmt.where(Workout.owner_id == owner_id)

    stmt = stmt.order_by(Workout.id.asc()).limit(limit).offset(offset)
    return list(session.scalars(stmt).all())

