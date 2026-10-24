"""Leakage-aware feature-based demand forecasting models."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from app.ml.baselines import ForecastingDataError, _metrics

REQUIRED_COLUMNS = {"date", "product_id", "market", "demand"}


def _make_features(series: pd.Series) -> pd.DataFrame:
    """Create features using only current/past demand and known calendar fields."""
    frame = pd.DataFrame(index=series.index)
    for lag in (1, 2, 3, 7, 14, 28):
        frame[f"lag_{lag}"] = series.shift(lag)
    shifted = series.shift(1)
    for window in (7, 14, 28):
        frame[f"rolling_mean_{window}"] = shifted.rolling(window).mean()
        frame[f"rolling_std_{window}"] = shifted.rolling(window).std().fillna(0.0)
    frame["day_of_week"] = frame.index.dayofweek
    frame["day_of_month"] = frame.index.day
    frame["month"] = frame.index.month
    frame["is_weekend"] = (frame.index.dayofweek >= 5).astype(int)
    return frame


def _features_for_next_date(history: pd.Series, forecast_date: pd.Timestamp) -> pd.DataFrame:
    """Build one feature row indexed by the date being forecast.

    A NaN target placeholder lets lag and rolling features use only history while
    calendar features correctly describe forecast_date.
    """
    forecast_date = pd.Timestamp(forecast_date).normalize()
    if forecast_date in history.index:
        raise ForecastingDataError("forecast_date must not already exist in history")
    if not history.index.is_monotonic_increasing or forecast_date <= history.index[-1]:
        raise ForecastingDataError("forecast_date must be later than the latest history date")
    placeholder = pd.Series([np.nan], index=pd.DatetimeIndex([forecast_date]), dtype=float)
    extended = pd.concat([history.astype(float), placeholder])
    return _make_features(extended).iloc[[-1]]


def walk_forward_ml_backtest(
    daily_demand: pd.DataFrame,
    *,
    product_id: str,
    market: str,
    horizon: int = 7,
    min_train_days: int = 56,
    step: int | None = None,
    fill_missing_days_with_zero: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Evaluate gradient boosting on rolling-origin, recursive forecasts."""
    missing = sorted(REQUIRED_COLUMNS.difference(daily_demand.columns))
    if missing:
        raise ForecastingDataError(
            "Demand data is missing required columns: " + ", ".join(missing)
        )
    if horizon < 1:
        raise ForecastingDataError("horizon must be at least 1")
    if min_train_days < 29:
        raise ForecastingDataError("min_train_days must be at least 29 for 28-day features")

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
        raise ForecastingDataError("Demand cannot be negative for this model target")

    observed = data.groupby("date")["demand"].sum().sort_index()
    calendar = pd.date_range(observed.index.min(), observed.index.max(), freq="D")
    if fill_missing_days_with_zero:
        series = observed.reindex(calendar, fill_value=0.0)
    else:
        series = observed.reindex(calendar)
        if series.isna().any():
            raise ForecastingDataError(
                "Selected series has missing calendar dates. Decide whether they "
                "mean zero sales or unavailable data before forecasting."
            )
    series.index = pd.DatetimeIndex(calendar)
    series = series.astype(float)

    step = horizon if step is None else step
    if step < 1:
        raise ForecastingDataError("step must be at least 1")
    origins = list(range(min_train_days, len(series) - horizon + 1, step))
    if not origins:
        raise ForecastingDataError(
            f"Need at least {min_train_days + horizon} calendar days; selected series has {len(series)}"
        )

    rows: list[dict[str, Any]] = []
    for origin in origins:
        history = series.iloc[:origin].copy()
        train_features = _make_features(history).iloc[28:]
        train_target = history.iloc[28:]
        valid = train_features.notna().all(axis=1)
        train_features, train_target = train_features.loc[valid], train_target.loc[valid]
        if len(train_features) < 10:
            raise ForecastingDataError("Not enough feature rows to train the ML model")

        model = HistGradientBoostingRegressor(
            max_iter=150,
            learning_rate=0.06,
            max_leaf_nodes=15,
            l2_regularization=1.0,
            random_state=42,
        )
        model.fit(train_features, train_target)

        origin_date = calendar[origin - 1].date().isoformat()
        actual_values = series.iloc[origin : origin + horizon].to_numpy(dtype=float)
        for offset in range(horizon):
            next_date = calendar[origin + offset]
            features = _features_for_next_date(history, next_date)
            prediction = max(0.0, float(model.predict(features)[0]))
            rows.append({
                "product_id": str(product_id),
                "market": str(market),
                "origin_date": origin_date,
                "date": next_date.date().isoformat(),
                "actual": float(actual_values[offset]),
                "ml_forecast": prediction,
            })
            history.loc[next_date] = prediction

    predictions = pd.DataFrame(rows)
    summary = {
        "model": "HistGradientBoostingRegressor",
        "product_id": str(product_id),
        "market": str(market),
        "horizon_days": int(horizon),
        "min_train_days": int(min_train_days),
        "backtest_origins": len(origins),
        "forecasted_observations": len(predictions),
        "calendar_start": calendar.min().date().isoformat(),
        "calendar_end": calendar.max().date().isoformat(),
        "missing_dates_filled_with_zero": bool(fill_missing_days_with_zero),
        "ml_model": _metrics(
            predictions["actual"].to_numpy(),
            predictions["ml_forecast"].to_numpy(),
        ),
        "note": (
            "Recursive multi-step forecast. Compare with baselines only on identical "
            "forecast origins and target dates. Missing calendar dates are zero-filled "
            "by default and this assumption should be validated for the selected series."
        ),
    }
    return predictions, summary
