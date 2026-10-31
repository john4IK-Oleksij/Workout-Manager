from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

ALLOWED_WORKOUT_KINDS = ("run", "gym", "yoga", "swim")


class User(Base):
    """ORM model representing an application user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    workouts: Mapped[list["Workout"]] = relationship(
        "Workout",
        back_populates="owner",
    )


class Workout(Base):
    """ORM model representing a user's workout."""

    __tablename__ = "workouts"
    __table_args__ = (
        CheckConstraint(
            "duration_min > 0",
            name="ck_workouts_duration_min_positive",
        ),
        CheckConstraint(
            "kind IN ('run', 'gym', 'yoga', 'swim')",
            name="ck_workouts_kind_allowed",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    kind: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    duration_min: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    distance_km: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )
    done_on: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="workouts",
    )
