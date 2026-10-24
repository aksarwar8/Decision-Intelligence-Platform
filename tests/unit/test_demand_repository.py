from datetime import date
import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.database.connection import Base
from app.database.models import DailyDemand
from app.database.repositories.demand import upsert_daily_demand

def test_upsert_is_idempotent_and_updates_existing_demand():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    rows = [{"date": pd.Timestamp("2016-01-01"), "product_id": "ITEM_1", "market": "STORE_1", "demand": 2.0}]
    with Session(engine) as session:
        assert upsert_daily_demand(session, rows) == (1, 1)
        assert upsert_daily_demand(session, [{**rows[0], "demand": 4.0}]) == (1, 1)
        saved = session.scalars(select(DailyDemand)).all()
        assert len(saved) == 1
        assert saved[0].date == date(2016, 1, 1)
        assert saved[0].demand == 4.0
    engine.dispose()
