
import pytest
from pydantic import ValidationError

from app.schemas.ingestion import IngestionRunCreate


def test_valid_ingestion_request():
    request = IngestionRunCreate(
        provider="m5_replay",
        mode="historical",
    )

    assert request.provider == "m5_replay"
    assert request.mode == "historical"


def test_invalid_mode_is_rejected():
    with pytest.raises(ValidationError):
        IngestionRunCreate(
            provider="m5_replay",
            mode="invalid",
        )


def test_missing_provider_is_rejected():
    with pytest.raises(ValidationError):
        IngestionRunCreate(
            mode="historical",
        )


def test_empty_provider_is_rejected():
    with pytest.raises(ValidationError):
        IngestionRunCreate(
            provider="",
            mode="historical",
        )
