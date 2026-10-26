
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base
from app.database.dependencies import get_db
from app.database.models import IngestionRun
from app.main import app


# Create an isolated in-memory database for tests.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)


def test_create_ingestion_run(client):
    response = client.post(
        "/api/v1/ingestion/runs",
        json={
            "provider": "test_provider",
            "mode": "historical",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["provider"] == "test_provider"
    assert data["mode"] == "historical"
    assert data["status"] == "pending"
    assert data["records_received"] == 0


def test_list_ingestion_runs(client):
    client.post(
        "/api/v1/ingestion/runs",
        json={
            "provider": "test_provider",
            "mode": "historical",
        },
    )

    response = client.get("/api/v1/ingestion/runs")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["provider"] == "test_provider"


def test_get_ingestion_run(client):
    created = client.post(
        "/api/v1/ingestion/runs",
        json={
            "provider": "test_provider",
            "mode": "incremental",
        },
    )

    run_id = created.json()["id"]
    response = client.get(f"/api/v1/ingestion/runs/{run_id}")

    assert response.status_code == 200
    assert response.json()["id"] == run_id
    assert response.json()["mode"] == "incremental"


def test_missing_ingestion_run_returns_404(client):
    response = client.get("/api/v1/ingestion/runs/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ingestion run not found"


def test_invalid_mode_returns_422(client):
    response = client.post(
        "/api/v1/ingestion/runs",
        json={
            "provider": "test_provider",
            "mode": "invalid",
        },
    )

    assert response.status_code == 422



def test_finish_ingestion_run(client):
    created = client.post(
        "/api/v1/ingestion/runs",
        json={
            "provider": "test_provider",
            "mode": "historical",
        },
    )
    assert created.status_code == 201
    run_id = created.json()["id"]

    from app.database.repositories.ingestion import finish_ingestion_run
    from app.database.dependencies import get_db

    # Use the same isolated database configured by the test fixture.
    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)

    try:
        run = finish_ingestion_run(
            db,
            run_id,
            status="completed",
            records_received=100,
            records_inserted=95,
            records_rejected=5,
        )

        assert run is not None
        assert run.status == "completed"
        assert run.records_received == 100
        assert run.records_inserted == 95
        assert run.records_rejected == 5
        assert run.completed_at is not None
    finally:
        db_generator.close()



def test_finish_ingestion_run_rejects_negative_counts(client):
    created = client.post(
        "/api/v1/ingestion/runs",
        json={
            "provider": "test_provider",
            "mode": "historical",
        },
    )
    run_id = created.json()["id"]

    from app.database.dependencies import get_db
    from app.database.repositories.ingestion import finish_ingestion_run

    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)

    try:
        with pytest.raises(ValueError, match="cannot be negative"):
            finish_ingestion_run(
                db,
                run_id,
                status="completed",
                records_received=100,
                records_inserted=-1,
                records_rejected=5,
            )
    finally:
        db_generator.close()


def test_finish_ingestion_run_rejects_excess_counts(client):
    created = client.post(
        "/api/v1/ingestion/runs",
        json={
            "provider": "test_provider",
            "mode": "historical",
        },
    )
    run_id = created.json()["id"]

    from app.database.dependencies import get_db
    from app.database.repositories.ingestion import finish_ingestion_run

    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)

    try:
        with pytest.raises(
            ValueError,
            match="cannot exceed received records",
        ):
            finish_ingestion_run(
                db,
                run_id,
                status="completed",
                records_received=100,
                records_inserted=95,
                records_rejected=10,
            )
    finally:
        db_generator.close()



def test_finish_ingestion_run_endpoint(client):
    created = client.post(
        "/api/v1/ingestion/runs",
        json={
            "provider": "test_provider",
            "mode": "historical",
        },
    )
    assert created.status_code == 201

    run_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/ingestion/runs/{run_id}/finish",
        json={
            "status": "completed",
            "records_received": 100,
            "records_inserted": 95,
            "records_rejected": 5,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["records_received"] == 100
    assert data["records_inserted"] == 95
    assert data["records_rejected"] == 5
    assert data["completed_at"] is not None


def test_finish_ingestion_run_endpoint_rejects_invalid_counts(client):
    created = client.post(
        "/api/v1/ingestion/runs",
        json={
            "provider": "test_provider",
            "mode": "historical",
        },
    )
    run_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/ingestion/runs/{run_id}/finish",
        json={
            "status": "completed",
            "records_received": 100,
            "records_inserted": 95,
            "records_rejected": 10,
        },
    )

    assert response.status_code == 422



def test_finish_ingestion_run_endpoint_returns_404_for_missing_run(client):
    response = client.patch(
        "/api/v1/ingestion/runs/999999/finish",
        json={
            "status": "completed",
            "records_received": 10,
            "records_inserted": 8,
            "records_rejected": 2,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ingestion run not found"


def test_finish_ingestion_run_endpoint_rejects_second_finish(client):
    created = client.post(
        "/api/v1/ingestion/runs",
        json={
            "provider": "test_provider",
            "mode": "historical",
        },
    )
    assert created.status_code == 201

    run_id = created.json()["id"]

    payload = {
        "status": "completed",
        "records_received": 10,
        "records_inserted": 8,
        "records_rejected": 2,
    }

    first_response = client.patch(
        f"/api/v1/ingestion/runs/{run_id}/finish",
        json=payload,
    )
    assert first_response.status_code == 200

    second_response = client.patch(
        f"/api/v1/ingestion/runs/{run_id}/finish",
        json=payload,
    )

    assert second_response.status_code == 409
    assert "Only pending ingestion runs can be finished" in (
        second_response.json()["detail"]
    )


def test_m5_replay_saves_selected_series(client, tmp_path, monkeypatch):
    import pandas as pd

    from app.core.config import settings

    pd.DataFrame(
        [{"item_id": "ITEM_1", "store_id": "STORE_1", "d_1": 3, "d_2": 0}]
    ).to_csv(tmp_path / "sales_train_validation.csv", index=False)
    pd.DataFrame(
        {"d": ["d_1", "d_2"], "date": ["2016-01-01", "2016-01-02"]}
    ).to_csv(tmp_path / "calendar.csv", index=False)
    monkeypatch.setattr(settings, "M5_DATA_DIRECTORY", str(tmp_path))

    response = client.post(
        "/api/v1/ingestion/m5/replay",
        json={"item_id": "ITEM_1", "store_id": "STORE_1"},
    )

    assert response.status_code == 201, response.text
    result = response.json()
    assert result["provider"] == "m5"
    assert result["status"] == "completed"
    assert result["records_received"] == 2
    assert result["records_inserted"] == 2


def test_m5_replay_marks_run_failed_when_files_are_missing(
    client, tmp_path, monkeypatch
):
    from app.core.config import settings

    monkeypatch.setattr(settings, "M5_DATA_DIRECTORY", str(tmp_path))

    response = client.post(
        "/api/v1/ingestion/m5/replay",
        json={"item_id": "ITEM_1", "store_id": "STORE_1"},
    )

    assert response.status_code == 422
    runs = client.get("/api/v1/ingestion/runs")
    assert runs.status_code == 200
    assert len(runs.json()) == 1
    assert runs.json()[0]["status"] == "failed"
