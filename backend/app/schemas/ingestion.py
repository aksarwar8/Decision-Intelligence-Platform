
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IngestionRunCreate(BaseModel):
    """Validate a request to start an ingestion run."""

    provider: str = Field(min_length=1, max_length=100)
    mode: Literal["historical", "incremental"]


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


class IngestionRunFinish(BaseModel):
    """Validate a request to finish an ingestion run."""

    status: Literal["completed", "failed"]
    records_received: int = Field(ge=0)
    records_inserted: int = Field(ge=0)
    records_rejected: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_record_counts(self):
        if self.records_inserted + self.records_rejected > self.records_received:
            raise ValueError(
                "Inserted and rejected counts cannot exceed received records"
            )
        return self
