from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    DoneRatioResponse,
    GroupBy,
    GroupStatsResponse,
    Metric,
    MonthlyStatsResponse,
    SummaryResponse,
    TopUserStatsResponse,
    WorkoutKindStats,
)
from app.services.stats_service import (
    get_done_ratio,
    get_group_stats,
    get_stats_by_kind,
    get_stats_by_month,
    get_summary,
    get_top_users,
)

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


@router.get(
    "/by-month",
    response_model=list[MonthlyStatsResponse],
)
def stats_by_month_endpoint(
    owner_id: Annotated[int, Query(gt=0)],
    session: Annotated[Session, Depends(get_db)],
) -> list[MonthlyStatsResponse]:
    """Get workout count and total distance per calendar month for a user."""
    return get_stats_by_month(session=session, owner_id=owner_id)


@router.get(
    "/top-users",
    response_model=list[TopUserStatsResponse],
)
def top_users_endpoint(
    session: Annotated[Session, Depends(get_db)],
    min_workouts: Annotated[int, Query(gt=0)] = 3,
) -> list[TopUserStatsResponse]:
    """Get users with at least min_workouts workouts, sorted by count descending."""
    return get_top_users(session=session, min_workouts=min_workouts)


@router.get(
    "/done-ratio",
    response_model=DoneRatioResponse,
)
def done_ratio_endpoint(
    owner_id: Annotated[int, Query(gt=0)],
    session: Annotated[Session, Depends(get_db)],
) -> DoneRatioResponse:
    """Get long workout count (>= 60 min) and total workout count for a user."""
    return get_done_ratio(session=session, owner_id=owner_id)


@router.get(
    "/group",
    response_model=list[GroupStatsResponse],
)
def group_stats_endpoint(
    group_by: GroupBy,
    metric: Metric,
    owner_id: Annotated[int, Query(gt=0)],
    session: Annotated[Session, Depends(get_db)],
) -> list[GroupStatsResponse]:
    """Get dynamic aggregation using whitelisted grouping column and metric."""
    return get_group_stats(
        session=session,
        group_by=group_by,
        metric=metric,
        owner_id=owner_id,
    )
