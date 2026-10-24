"""Load and prepare the UCI Online Retail workbook for demand analysis.

The source data is transaction-line data, not a store/day demand table. This
module converts valid positive sales lines into daily product-by-country demand.
Returns and cancellation invoices are excluded from the demand target and
reported in the quality summary rather than silently mixed into demand.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = {
    "InvoiceNo",
    "StockCode",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "Country",
}


class OnlineRetailDataError(ValueError):
    """Raised when an Online Retail source cannot be interpreted safely."""


def load_online_retail(
    path: str | Path,
    *,
    sheet_name: str = "Online Retail",
) -> pd.DataFrame:
    """Read and validate the expected worksheet from an Excel workbook."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Online Retail workbook not found: {source}")

    try:
        frame = pd.read_excel(source, sheet_name=sheet_name, engine="openpyxl")
    except ValueError as exc:
        raise OnlineRetailDataError(
            f"Worksheet {sheet_name!r} was not found in {source.name}"
        ) from exc

    missing = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing:
        raise OnlineRetailDataError(
            "Workbook is missing required columns: " + ", ".join(missing)
        )

    return frame


def prepare_daily_demand(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Aggregate transaction lines into daily product-by-country demand.

    Returns:
        A tuple of (daily demand DataFrame, quality summary).
        Output columns are date, product_id, market, demand, revenue,
        transaction_count, and product_name.

    Policy:
        * Positive-quantity sales are demand.
        * Cancellation invoices (InvoiceNo beginning with C) are excluded.
        * Zero/negative quantities (typically returns/corrections) are excluded.
        * Invalid dates, nonnumeric quantity/price, and missing product IDs are
          excluded and counted in the quality summary.
        * Country is used as the market dimension because this dataset has no
          store identifier.
    """
    missing = sorted(REQUIRED_COLUMNS.difference(raw.columns))
    if missing:
        raise OnlineRetailDataError(
            "Input data is missing required columns: " + ", ".join(missing)
        )
    if raw.empty:
        raise OnlineRetailDataError("Input workbook contains no transaction rows")

    frame = raw.copy()
    row_count = len(frame)

    invoice = frame["InvoiceNo"].astype("string").str.strip()
    is_cancellation = invoice.str.upper().str.startswith("C", na=False)
    frame["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"], errors="coerce")
    frame["Quantity"] = pd.to_numeric(frame["Quantity"], errors="coerce")
    frame["UnitPrice"] = pd.to_numeric(frame["UnitPrice"], errors="coerce")

    invalid_date = frame["InvoiceDate"].isna()
    invalid_quantity = frame["Quantity"].isna()
    invalid_price = frame["UnitPrice"].isna()
    missing_product = frame["StockCode"].isna() | (
        frame["StockCode"].astype("string").str.strip() == ""
    )
    nonpositive_quantity = frame["Quantity"].le(0).fillna(False)
    negative_price = frame["UnitPrice"].lt(0).fillna(False)

    valid = (
        ~invalid_date
        & ~invalid_quantity
        & ~invalid_price
        & ~missing_product
        & ~is_cancellation
        & ~nonpositive_quantity
        & ~negative_price
    )

    accepted = frame.loc[valid].copy()
    if accepted.empty:
        raise OnlineRetailDataError(
            "No valid positive sales rows remain after applying data-quality rules"
        )

    accepted["date"] = accepted["InvoiceDate"].dt.normalize()
    accepted["product_id"] = accepted["StockCode"].astype("string").str.strip()
    accepted["market"] = (
        accepted["Country"].astype("string").str.strip().replace("", pd.NA).fillna("Unknown")
    )
    accepted["revenue"] = accepted["Quantity"] * accepted["UnitPrice"]
    accepted["product_name"] = (
        accepted["Description"].astype("string").str.strip()
        if "Description" in accepted.columns
        else pd.Series(pd.NA, index=accepted.index, dtype="string")
    )

    daily = (
        accepted.groupby(["date", "product_id", "market"], as_index=False, dropna=False)
        .agg(
            demand=("Quantity", "sum"),
            revenue=("revenue", "sum"),
            transaction_count=("InvoiceNo", "nunique"),
            product_name=("product_name", "first"),
        )
        .sort_values(["date", "product_id", "market"])
        .reset_index(drop=True)
    )

    quality: dict[str, Any] = {
        "source_rows": int(row_count),
        "invalid_dates": int(invalid_date.sum()),
        "nonnumeric_quantities": int(invalid_quantity.sum()),
        "nonnumeric_prices": int(invalid_price.sum()),
        "missing_product_ids": int(missing_product.sum()),
        "cancellation_invoices": int(is_cancellation.sum()),
        "nonpositive_quantity_rows": int(nonpositive_quantity.sum()),
        "negative_price_rows": int(negative_price.sum()),
        "accepted_sales_rows": int(valid.sum()),
        "daily_demand_rows": int(len(daily)),
        "total_units_sold": float(daily["demand"].sum()),
        "total_sales_revenue": float(daily["revenue"].sum()),
        "date_min": str(daily["date"].min().date()),
        "date_max": str(daily["date"].max().date()),
        "product_count": int(daily["product_id"].nunique()),
        "market_count": int(daily["market"].nunique()),
    }
    return daily, quality
