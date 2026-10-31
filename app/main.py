
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine, init_db

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Workout Tracking API")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize database tables on startup."""
    init_db()
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Check API and database availability."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "application": APP_NAME,
            "database": "connected",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable",
        )
