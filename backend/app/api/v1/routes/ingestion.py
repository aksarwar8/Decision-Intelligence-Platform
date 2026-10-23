

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.ingestion import IngestionRunCreate, IngestionRunResponse
from app.services.ingestion_service import (
    get_ingestion_run_by_id,
    get_ingestion_runs,
    start_ingestion_run,
)



router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"],
)


@router.post(
    "/runs",
    response_model=IngestionRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ingestion_run_endpoint(
    request: IngestionRunCreate,
    db: Session = Depends(get_db),
) -> IngestionRunResponse:
    """Create an ingestion-run record."""
    return start_ingestion_run(db, request)


@router.get(
    "/runs",
    response_model=list[IngestionRunResponse],
)
def list_ingestion_runs_endpoint(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[IngestionRunResponse]:
    """List ingestion runs, newest first."""
    return get_ingestion_runs(
        db,
        limit=limit,
        offset=offset,
    )



@router.get(
    "/runs/{run_id}",
    response_model=IngestionRunResponse,
)
def get_ingestion_run_endpoint(
    run_id: int,
    db: Session = Depends(get_db),
) -> IngestionRunResponse:
    """Retrieve one ingestion run by ID."""
    run = get_ingestion_run_by_id(db, run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Ingestion run not found",
        )

    return run

