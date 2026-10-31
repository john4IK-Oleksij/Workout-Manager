from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SummaryResponse, WorkoutKindStats
from app.services.stats_service import get_stats_by_kind, get_summary

router = APIRouter()


@router.get(
    "/summary",
    response_model=SummaryResponse,
)
def summary_stats_endpoint(
    owner_id: Annotated[int, Query(gt=0)],
    session: Annotated[Session, Depends(get_db)],
) -> SummaryResponse:
    """Get summary statistics for a user's workouts."""
    return get_summary(session=session, owner_id=owner_id)


@router.get(
    "/by-kind",
    response_model=list[WorkoutKindStats],
)
def stats_by_kind_endpoint(
    owner_id: Annotated[int, Query(gt=0)],
    session: Annotated[Session, Depends(get_db)],
) -> list[WorkoutKindStats]:
    """Get workout statistics grouped by workout kind for a user."""
    return get_stats_by_kind(session=session, owner_id=owner_id)

