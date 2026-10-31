from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Workout
from app.schemas import WorkoutCreate, WorkoutResponse
from app.services.workouts_service import create_workout, get_workouts

router = APIRouter(prefix="/workouts", tags=["Workouts"])


@router.post(
    "",
    response_model=WorkoutResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workout_endpoint(
    workout_data: WorkoutCreate,
    session: Annotated[Session, Depends(get_db)],
) -> Workout:
    """Create a new workout for an existing user."""
    return create_workout(session=session, workout_data=workout_data)


@router.get(
    "",
    response_model=list[WorkoutResponse],
    status_code=status.HTTP_200_OK,
)
def list_workouts_endpoint(
    session: Annotated[Session, Depends(get_db)],
    owner_id: Annotated[int | None, Query(gt=0)] = None,
    limit: Annotated[int, Query(gt=0, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Workout]:
    """Get a paginated list of workouts, optionally filtered by owner_id."""
    return get_workouts(
        session=session,
        owner_id=owner_id,
        limit=limit,
        offset=offset,
    )

