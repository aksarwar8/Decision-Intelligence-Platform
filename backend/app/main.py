
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.routes.ingestion import router as ingestion_router

from app.core.config import settings
from app.database.connection import engine

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A retail demand forecasting and decision intelligence platform.",
)
app.include_router(ingestion_router, prefix="/api/v1")

@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    """Return basic information about the application."""
    return {
        "message": "Welcome to DecisionOS",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Check the application and database health."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "unavailable",
            },
        )

    return {
        "status": "healthy",
        "database": "connected",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
