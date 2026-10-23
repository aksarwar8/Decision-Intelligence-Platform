
import pytest
from pydantic import ValidationError

from app.schemas.ingestion import IngestionRunCreate


def test_valid_ingestion_request():
    request = IngestionRunCreate(
        provider="m5_replay",
        mode="historical",
        records_received=100,
    )

    assert request.provider == "m5_replay"
    assert request.mode == "historical"
    assert request.records_received == 100
    assert request.records_inserted == 0
    assert request.records_rejected == 0


def test_invalid_mode_is_rejected():
    with pytest.raises(ValidationError):
        IngestionRunCreate(
            provider="m5_replay",
            mode="invalid",
        )


def test_negative_record_count_is_rejected():
    with pytest.raises(ValidationError):
        IngestionRunCreate(
            provider="m5_replay",
            mode="historical",
            records_received=-1,
        )


def test_empty_provider_is_rejected():
    with pytest.raises(ValidationError):
        IngestionRunCreate(
            provider="",
            mode="historical",
        )
