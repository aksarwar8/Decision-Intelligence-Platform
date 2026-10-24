"""Load M5 sales and calendar CSVs into DecisionOS daily-demand format."""
from __future__ import annotations

from pathlib import Path
import pandas as pd


class M5DataError(ValueError):
    """Raised when M5 files cannot be interpreted safely."""


def load_m5_daily_demand(sales_path: str | Path, calendar_path: str | Path, *,
                         item_id: str | None = None,
                         store_id: str | None = None) -> pd.DataFrame:
    """Return date/product_id/market/demand rows; market represents M5 store_id."""
    sales_file, calendar_file = Path(sales_path), Path(calendar_path)
    if not sales_file.is_file():
        raise FileNotFoundError(f"M5 sales file not found: {sales_file}")
    if not calendar_file.is_file():
        raise FileNotFoundError(f"M5 calendar file not found: {calendar_file}")
    try:
        sales = pd.read_csv(sales_file)
        calendar = pd.read_csv(calendar_file, usecols=["d", "date"])
    except (ValueError, pd.errors.ParserError) as exc:
        raise M5DataError(f"Could not read required M5 columns: {exc}") from exc

    missing_ids = sorted({"item_id", "store_id"}.difference(sales.columns))
    if missing_ids:
        raise M5DataError("M5 sales file is missing columns: " + ", ".join(missing_ids))
    day_columns = [column for column in sales.columns if column.startswith("d_")]
    if not day_columns:
        raise M5DataError("M5 sales file contains no daily columns named d_1, d_2, ...")
    if calendar["d"].duplicated().any():
        raise M5DataError("M5 calendar contains duplicate day IDs")
    missing_days = sorted(set(day_columns).difference(calendar["d"].astype(str)))
    if missing_days:
        raise M5DataError("M5 calendar is missing sales day IDs: " + ", ".join(missing_days[:5]))

    if item_id is not None:
        sales = sales.loc[sales["item_id"].astype(str) == str(item_id)]
    if store_id is not None:
        sales = sales.loc[sales["store_id"].astype(str) == str(store_id)]
    if sales.empty:
        raise M5DataError(f"No M5 rows found for item_id={item_id!r}, store_id={store_id!r}")

    selected = sales[["item_id", "store_id", *day_columns]].copy()
    for column in day_columns:
        selected[column] = pd.to_numeric(selected[column], errors="coerce")
    if selected[day_columns].isna().any().any():
        raise M5DataError("M5 daily sales columns contain missing or nonnumeric values")
    if (selected[day_columns] < 0).any().any():
        raise M5DataError("M5 daily sales values cannot be negative")

    long = selected.melt(id_vars=["item_id", "store_id"], value_vars=day_columns,
                         var_name="d", value_name="demand")
    date_lookup = calendar.copy()
    date_lookup["date"] = pd.to_datetime(date_lookup["date"], errors="coerce")
    if date_lookup["date"].isna().any():
        raise M5DataError("M5 calendar contains invalid dates")
    long = long.merge(date_lookup[["d", "date"]], on="d", how="left", validate="many_to_one")
    if long["date"].isna().any():
        raise M5DataError("Some M5 day IDs could not be mapped to calendar dates")
    result = long.rename(columns={"item_id": "product_id", "store_id": "market"})
    result = result[["date", "product_id", "market", "demand"]]
    result = result.sort_values(["date", "product_id", "market"]).reset_index(drop=True)
    result["product_id"] = result["product_id"].astype(str)
    result["market"] = result["market"].astype(str)
    result["demand"] = result["demand"].astype(float)
    return result
