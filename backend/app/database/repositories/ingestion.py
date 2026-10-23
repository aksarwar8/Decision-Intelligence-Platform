
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import IngestionRun


def create_ingestion_run(
    db: Session,
    *,
    provider: str,
    mode: str,
    status: str,
    records_received: int = 0,
    records_inserted: int = 0,
    records_rejected: int = 0,
) -> IngestionRun:
    """Create and save an ingestion-run record."""
    now = datetime.now(timezone.utc)

    run = IngestionRun(
        provider=provider,
        mode=mode,
        status=status,
        records_received=records_received,
        records_inserted=records_inserted,
        records_rejected=records_rejected,
        started_at=now,
        completed_at=now if status == "completed" else None,
    )

    try:
        db.add(run)
        db.commit()
        db.refresh(run)
        return run
    except Exception:
        db.rollback()
        raise


def list_ingestion_runs(
    db: Session,
    *,
    limit: int = 100,
    offset: int = 0,
) -> list[IngestionRun]:
    """Return ingestion runs, newest first."""
    statement = (
        select(IngestionRun)
        .order_by(IngestionRun.id.desc())
        .limit(limit)
        .offset(offset)
    )

    return list(db.scalars(statement).all())



def get_ingestion_run(
    db: Session,
    run_id: int,
) -> IngestionRun | None:
    """Retrieve one ingestion run by ID."""
    return db.get(IngestionRun, run_id)

