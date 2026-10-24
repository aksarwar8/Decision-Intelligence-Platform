"""Replay a selected M5 item/store series from local raw CSV files."""
from pathlib import Path
import pandas as pd
from app.core.config import settings
from app.data.m5 import load_m5_daily_demand

class M5ReplayProvider:
    """Read the configured M5 sales/calendar files for one series."""
    name = "m5_replay"

    def __init__(self, data_directory: str | Path | None = None) -> None:
        self.data_directory = Path(data_directory or settings.M5_DATA_DIRECTORY)

    def load(self, *, item_id: str, store_id: str) -> pd.DataFrame:
        if not item_id.strip() or not store_id.strip():
            raise ValueError("item_id and store_id are required for M5 replay")
        return load_m5_daily_demand(
            self.data_directory / "sales_train_validation.csv",
            self.data_directory / "calendar.csv",
            item_id=item_id, store_id=store_id)
