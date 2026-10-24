from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.dependencies import get_db
from app.database.repositories.demand import upsert_daily_demand
from app.database.repositories.ingestion import create_ingestion_run
from app.providers.m5_replay import M5ReplayProvider
from app.schemas.ingestion import IngestionRunCreate, IngestionRunFinish, IngestionRunResponse, M5ReplayRequest
from app.services.ingestion_service import complete_ingestion_run, get_ingestion_run_by_id, get_ingestion_runs, start_ingestion_run

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

@router.post("/runs", response_model=IngestionRunResponse, status_code=status.HTTP_201_CREATED)
def create_ingestion_run_endpoint(request: IngestionRunCreate, db: Session = Depends(get_db)) -> IngestionRunResponse:
    """Create an ingestion-run record."""
    return start_ingestion_run(db, request)

@router.get("/runs", response_model=list[IngestionRunResponse])
def list_ingestion_runs_endpoint(db: Session = Depends(get_db), limit: int = Query(default=100, ge=1, le=500), offset: int = Query(default=0, ge=0)) -> list[IngestionRunResponse]:
    """List ingestion runs, newest first."""
    return get_ingestion_runs(db, limit=limit, offset=offset)

@router.get("/runs/{run_id}", response_model=IngestionRunResponse)
def get_ingestion_run_endpoint(run_id: int, db: Session = Depends(get_db)) -> IngestionRunResponse:
    """Retrieve one ingestion run by ID."""
    run = get_ingestion_run_by_id(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return run

@router.patch("/runs/{run_id}/finish", response_model=IngestionRunResponse)
def finish_ingestion_run_endpoint(run_id: int, request: IngestionRunFinish, db: Session = Depends(get_db)) -> IngestionRunResponse:
    """Finish a pending ingestion run."""
    try:
        run = complete_ingestion_run(db, run_id, status=request.status, records_received=request.records_received, records_inserted=request.records_inserted, records_rejected=request.records_rejected)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if run is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return run

@router.post("/m5/replay", response_model=IngestionRunResponse, status_code=status.HTTP_201_CREATED)
def replay_m5_endpoint(request: M5ReplayRequest, db: Session = Depends(get_db)) -> IngestionRunResponse:
    """Load one M5 item/store series and persist it idempotently."""
    run = create_ingestion_run(db, provider=M5ReplayProvider.name, mode="historical", status="pending")
    try:
        demand = M5ReplayProvider(settings.M5_DATA_DIRECTORY).load(item_id=request.item_id, store_id=request.store_id)
        received, inserted_or_updated = upsert_daily_demand(db, demand.to_dict(orient="records"))
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
        run = db.get(type(run), run.id)
        if run is not None:
            run.status = "failed"
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        run = db.get(type(run), run.id)
        if run is not None:
            run.status = "failed"
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
        raise HTTPException(status_code=500, detail="M5 ingestion failed; see server logs") from exc
