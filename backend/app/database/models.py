from datetime import date, datetime
from sqlalchemy import Date, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database.connection import Base

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    records_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class DailyDemand(Base):
    """Canonical daily demand observations keyed by date, product and market."""
    __tablename__ = "daily_demand"
    __table_args__ = (UniqueConstraint("date", "product_id", "market", name="uq_daily_demand_series_date"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    market: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    demand: Mapped[float] = mapped_column(Float, nullable=False)
