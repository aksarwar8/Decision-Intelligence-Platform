
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import IngestionRun


class IngestionRunCreate(BaseModel):
    """Validate data submitted to create an ingestion run."""

    provider: str = Field(min_length=1, max_length=100)
    mode: Literal["historical", "incremental"]
    records_received: int = Field(default=0, ge=0)
    records_inserted: int = Field(default=0, ge=0)
    records_rejected: int = Field(default=0, ge=0)


class IngestionRunResponse(BaseModel):
    """Define the data returned for an ingestion run."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: str
    mode: str
    status: str
    records_received: int
    records_inserted: int
    records_rejected: int
    started_at: datetime
    completed_at: datetime | None



