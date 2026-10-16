from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    provider: Mapped[str] = mapped_column(String(100), nullable=False)

    mode: Mapped[str] = mapped_column(String(20), nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False)

    records_received: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    records_inserted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    records_rejected: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )