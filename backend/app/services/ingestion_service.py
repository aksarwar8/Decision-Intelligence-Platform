
from sqlalchemy.orm import Session

from app.database.models import IngestionRun
from app.database.repositories.ingestion import create_ingestion_run
from app.schemas.ingestion import IngestionRunCreate
from app.database.repositories.ingestion import list_ingestion_runs
from app.database.repositories.ingestion import get_ingestion_run

from app.database.repositories.ingestion import finish_ingestion_run


def start_ingestion_run(
    db: Session,
    request: IngestionRunCreate,
) -> IngestionRun:
    """Create a pending ingestion run."""
    return create_ingestion_run(
        db,
        provider=request.provider,
        mode=request.mode,
        status="pending",
    )



def get_ingestion_runs(
    db: Session,
    *,
    limit: int = 100,
    offset: int = 0,
) -> list[IngestionRun]:
    """Retrieve ingestion runs through the repository."""
    return list_ingestion_runs(
        db,
        limit=limit,
        offset=offset,
    )



def get_ingestion_run_by_id(
    db: Session,
    run_id: int,
) -> IngestionRun | None:
    """Retrieve one ingestion run by ID."""
    return get_ingestion_run(db, run_id)



def complete_ingestion_run(
    db: Session,
    run_id: int,
    *,
    status: str,
    records_received: int,
    records_inserted: int,
    records_rejected: int,
) -> IngestionRun | None:
    """Finish an ingestion run through the repository."""
    return finish_ingestion_run(
        db,
        run_id,
        status=status,
        records_received=records_received,
        records_inserted=records_inserted,
        records_rejected=records_rejected,
    )
