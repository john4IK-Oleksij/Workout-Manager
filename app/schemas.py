from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class WorkoutKind(StrEnum):
    """Allowed workout types."""

    RUN = "run"
    GYM = "gym"
    YOGA = "yoga"
    SWIM = "swim"


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=255)


class UserResponse(BaseModel):
    """Schema for returning user data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class WorkoutCreate(BaseModel):
    """Schema for creating a new workout."""

    model_config = ConfigDict(extra="forbid")

    owner_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=100)
    kind: WorkoutKind
    duration_min: int = Field(..., gt=0)
    distance_km: Decimal = Field(
        ...,
        ge=Decimal("0.00"),
        max_digits=6,
        decimal_places=2,
    )
    done_on: date

    @field_validator("distance_km", mode="before")
    @classmethod
    def normalize_float_distance(cls, value: Any) -> Any:
        """Convert float inputs to string before Decimal parsing to avoid float precision issues."""
        if isinstance(value, float):
            return str(value)
        return value


class WorkoutResponse(BaseModel):
    """Schema for returning workout data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    title: str
    kind: WorkoutKind
    duration_min: int
    distance_km: Decimal
    done_on: date


class SummaryResponse(BaseModel):
    """Schema for overall user workout summary statistics."""

    owner_id: int
    total_workouts: int
    total_minutes: int
    total_km: Decimal
    avg_duration: Decimal | float | None
    min_distance: Decimal | None
    max_distance: Decimal | None


class MonthlyStatsResponse(BaseModel):
    """Schema for workout statistics grouped by calendar month."""

    month: str
    workouts_count: int
    total_distance_km: Decimal


class TopUserStatsResponse(BaseModel):
    """Schema for a user with their workout count."""

    user_id: int
    name: str
    workouts_count: int


class DoneRatioResponse(BaseModel):
    """Schema for long workout count versus total workout count."""

    owner_id: int
    long_workouts_count: int
    total_workouts_count: int


class GroupBy(StrEnum):
    """Allowed grouping fields for dynamic aggregation."""

    KIND = "kind"
    OWNER_ID = "owner_id"


class Metric(StrEnum):
    """Allowed aggregate metrics for dynamic aggregation."""

    COUNT = "count"
    SUM_DURATION = "sum_duration"
    SUM_DISTANCE = "sum_distance"
    AVG_DURATION = "avg_duration"


class GroupStatsResponse(BaseModel):
    """Schema for one group of a dynamic aggregation result."""

    group_value: int | str
    metric: Metric
    value: int | Decimal | None


class RunningTotalResponse(BaseModel):
    """Schema for one workout with cumulative distance."""

    done_on: date
    distance_km: Decimal
    running_total_km: Decimal


class WorkoutKindRankResponse(BaseModel):
    """Schema for a workout kind ranked by total duration."""

    kind: WorkoutKind
    total_duration_min: int
    rank: int


class WorkoutKindStats(BaseModel):
    """Schema for workout statistics grouped by workout kind."""

    kind: WorkoutKind
    workout_count: int
    total_minutes: int
    total_km: Decimal
