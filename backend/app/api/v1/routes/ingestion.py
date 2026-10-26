"""Ingestion API endpoints.

Each endpoint validates the request and coordinates the small steps needed to
load data. Data parsing lives in app.data; database operations live in
app.database.repositories.
"""
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.data.m5 import load_m5_daily_demand
from app.database.dependencies import get_db
from app.database.models import IngestionRun
from app.database.repositories.demand import upsert_daily_demand
from app.database.repositories.ingestion import (
    create_ingestion_run,
    finish_ingestion_run,
    get_ingestion_run,
    list_ingestion_runs,
)
from app.schemas.ingestion import (
    IngestionRunCreate,
    IngestionRunFinish,
    IngestionRunResponse,
    M5ReplayRequest,
)

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


@router.post(
    "/runs",
    response_model=IngestionRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ingestion_run_endpoint(
    request: IngestionRunCreate,
    db: Session = Depends(get_db),
) -> IngestionRunResponse:
    """Create a pending ingestion-run record."""
    return create_ingestion_run(
        db,
        provider=request.provider,
        mode=request.mode,
        status="pending",
    )


@router.get("/runs", response_model=list[IngestionRunResponse])
def list_ingestion_runs_endpoint(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[IngestionRun]:
    """List ingestion runs, newest first."""
    return list_ingestion_runs(db, limit=limit, offset=offset)


@router.get("/runs/{run_id}", response_model=IngestionRunResponse)
def get_ingestion_run_endpoint(
    run_id: int,
    db: Session = Depends(get_db),
) -> IngestionRunResponse:
    """Return one ingestion-run record."""
    run = get_ingestion_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return run


@router.patch("/runs/{run_id}/finish", response_model=IngestionRunResponse)
def finish_ingestion_run_endpoint(
    run_id: int,
    request: IngestionRunFinish,
    db: Session = Depends(get_db),
) -> IngestionRunResponse:
    """Finish a pending ingestion run."""
    try:
        run = finish_ingestion_run(
            db,
            run_id,
            status=request.status,
            records_received=request.records_received,
            records_inserted=request.records_inserted,
            records_rejected=request.records_rejected,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if run is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return run


@router.post(
    "/m5/replay",
    response_model=IngestionRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def replay_m5_endpoint(
    request: M5ReplayRequest,
    db: Session = Depends(get_db),
) -> IngestionRunResponse:
    """Load one M5 item/store series and save its daily demand.

    A replay is limited to one series so that a request does not load the full
    M5 dataset into memory. Demand rows and the successful run status are
    committed together.
    """
    run = create_ingestion_run(
        db,
        provider="m5",
        mode="historical",
        status="pending",
    )
    data_directory = Path(settings.M5_DATA_DIRECTORY)

    try:
        demand = load_m5_daily_demand(
            data_directory / "sales_train_validation.csv",
            data_directory / "calendar.csv",
            item_id=request.item_id,
            store_id=request.store_id,
        )
        received, inserted_or_updated = upsert_daily_demand(
            db,
            demand.to_dict(orient="records"),
            commit=False,
        )

        # Keep the demand rows and successful run status in one transaction.
        run = get_ingestion_run(db, run.id)
        if run is None:
            raise RuntimeError("Ingestion-run record disappeared during replay")

        run.status = "completed"
        run.records_received = received
        run.records_inserted = inserted_or_updated
        run.records_rejected = 0
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(run)
        return run

    except (FileNotFoundError, ValueError) as exc:
        db.rollback()
        _mark_run_failed(db, run.id)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        _mark_run_failed(db, run.id)
        raise HTTPException(
            status_code=500,
            detail="M5 ingestion failed; see server logs",
        ) from exc


def _mark_run_failed(db: Session, run_id: int) -> None:
    """Persist a failed status after rolling back the attempted data write."""
    run = get_ingestion_run(db, run_id)
    if run is None:
        return
    run.status = "failed"
    run.completed_at = datetime.now(timezone.utc)
    db.commit()
