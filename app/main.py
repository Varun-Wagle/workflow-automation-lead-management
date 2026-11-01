from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.leads import router as leads_router

from app.database import engine


app = FastAPI(
    title="Lead Management API",
    description="API for lead intake and sales follow-up automation.",
    version="0.1.0",
)

app.include_router(leads_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return the API process health status."""
    return {"status": "ok"}


@app.get("/health/db", tags=["Health"])
def database_health_check() -> dict[str, str]:
    """Check whether PostgreSQL is reachable."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"status": "ok", "database": "connected"}

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "database": "unavailable",
            },
        ) from exc