"""Simple, leakage-aware forecasting baselines and walk-forward evaluation."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {"date", "product_id", "market", "demand"}


class ForecastingDataError(ValueError):
    """Raised when demand data is insufficient or malformed."""


def _metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float | None]:
    errors = actual - predicted
    absolute_error = np.abs(errors)
    denominator = float(np.abs(actual).sum())
    wape = float(absolute_error.sum() / denominator * 100.0) if denominator else None
    return {
        "mae": float(absolute_error.mean()),
        "rmse": float(np.sqrt(np.mean(np.square(errors)))),
        "wape_percent": wape,
    }


def walk_forward_baseline_backtest(
    daily_demand: pd.DataFrame,
    *,
    product_id: str,
    market: str,
    horizon: int = 7,
    min_train_days: int = 28,
    step: int | None = None,
    fill_missing_days_with_zero: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Compare last-value and weekly seasonal-naive forecasts on rolling origins.

    Each forecast origin sees only dates strictly before its forecast window.
    The function expects one product/market series, represented by the columns
    date, product_id, market, and demand.

    Missing calendar dates can be filled with zero only when the caller accepts
    the assumption that no recorded sales means zero demand. Set the option to
    False to preserve missing dates and fail clearly rather than silently
    imputing them.
    """
    missing = sorted(REQUIRED_COLUMNS.difference(daily_demand.columns))
    if missing:
        raise ForecastingDataError(
            "Demand data is missing required columns: " + ", ".join(missing)
        )
    if horizon < 1:
        raise ForecastingDataError("horizon must be at least 1")
    if min_train_days < max(7, horizon):
        raise ForecastingDataError("min_train_days must be at least max(7, horizon)")

    data = daily_demand.loc[
        (daily_demand["product_id"].astype(str) == str(product_id))
        & (daily_demand["market"].astype(str) == str(market)),
        ["date", "demand"],
    ].copy()
    if data.empty:
        raise ForecastingDataError(
            f"No demand records found for product_id={product_id!r}, market={market!r}"
        )

    data["date"] = pd.to_datetime(data["date"], errors="coerce").dt.normalize()
    data["demand"] = pd.to_numeric(data["demand"], errors="coerce")
    data = data.dropna(subset=["date", "demand"])
    if data.empty:
        raise ForecastingDataError("Selected series has no valid date/demand values")
    if (data["demand"] < 0).any():
        raise ForecastingDataError("Demand cannot be negative for this baseline target")

    # There should be only one aggregate value per date/product/market.
    data = data.groupby("date", as_index=True)["demand"].sum().sort_index()
    calendar = pd.date_range(data.index.min(), data.index.max(), freq="D")
    if fill_missing_days_with_zero:
        series = data.reindex(calendar, fill_value=0.0)
    else:
        series = data.reindex(calendar)
        if series.isna().any():
            raise ForecastingDataError(
                "Selected series has missing calendar dates. Decide whether they "
                "mean zero sales or unavailable data before forecasting."
            )
    values = series.to_numpy(dtype=float)

    step = horizon if step is None else step
    if step < 1:
        raise ForecastingDataError("step must be at least 1")
    last_origin = len(values) - horizon
    origins = list(range(min_train_days, last_origin + 1, step))
    if not origins:
        raise ForecastingDataError(
            f"Need at least {min_train_days + horizon} calendar days; "
            f"selected series has {len(values)}"
        )

    rows: list[dict[str, Any]] = []
    for origin in origins:
        train = values[:origin]
        target_dates = calendar[origin : origin + horizon]
        actual = values[origin : origin + horizon]
        naive = np.repeat(train[-1], horizon)
        seasonal = np.resize(train[-7:], horizon)

        for i, target_date in enumerate(target_dates):
            rows.append({
                "product_id": str(product_id),
                "market": str(market),
                "origin_date": calendar[origin - 1].date().isoformat(),
                "date": target_date.date().isoformat(),
                "actual": float(actual[i]),
                "naive_forecast": float(naive[i]),
                "seasonal_naive_forecast": float(seasonal[i]),
            })

    predictions = pd.DataFrame(rows)
    summary = {
        "product_id": str(product_id),
        "market": str(market),
        "horizon_days": int(horizon),
        "min_train_days": int(min_train_days),
        "backtest_origins": len(origins),
        "forecasted_observations": len(predictions),
        "calendar_start": calendar.min().date().isoformat(),
        "calendar_end": calendar.max().date().isoformat(),
        "missing_dates_filled_with_zero": bool(fill_missing_days_with_zero),
        "naive": _metrics(
            predictions["actual"].to_numpy(),
            predictions["naive_forecast"].to_numpy(),
        ),
        "seasonal_naive": _metrics(
            predictions["actual"].to_numpy(),
            predictions["seasonal_naive_forecast"].to_numpy(),
        ),
        "interpretation": (
            "Metrics aggregate rolling-origin forecasts. Choose a model only after "
            "comparing on the same forecast windows; lower MAE/RMSE/WAPE is better. "
            "WAPE is unavailable when all evaluated actual demand is zero."
        ),
    }
    return predictions, summary
