"""Persistence helpers for canonical daily demand observations."""
from datetime import date
from typing import Iterable
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import DailyDemand

def upsert_daily_demand(db: Session, rows: Iterable[dict]) -> tuple[int, int]:
    """Insert or update observations; return (received, inserted_or_updated)."""
    received = changed = 0
    try:
        for row in rows:
            received += 1
            observation_date = row["date"]
            if not isinstance(observation_date, date):
                observation_date = observation_date.date()
            existing = db.scalar(select(DailyDemand).where(
                DailyDemand.date == observation_date,
                DailyDemand.product_id == str(row["product_id"]),
                DailyDemand.market == str(row["market"])))
            if existing is None:
                db.add(DailyDemand(date=observation_date, product_id=str(row["product_id"]),
                                   market=str(row["market"]), demand=float(row["demand"])))
            else:
                existing.demand = float(row["demand"])
            changed += 1
        db.commit()
        return received, changed
    except Exception:
        db.rollback()
        raise
