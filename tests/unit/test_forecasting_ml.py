import pandas as pd
import pytest

from app.ml.baselines import ForecastingDataError
from app.ml.forecasting import _features_for_next_date, walk_forward_ml_backtest


def frame(values):
    dates = pd.date_range("2024-01-01", periods=len(values), freq="D")
    return pd.DataFrame({
        "date": dates,
        "product_id": "P1",
        "market": "UK",
        "demand": values,
    })


def test_forecast_features_are_aligned_to_next_date_and_use_past_values_only():
    dates = pd.date_range("2024-01-01", periods=35, freq="D")
    history = pd.Series([float(i + 1) for i in range(35)], index=dates)
    forecast_date = dates[-1] + pd.Timedelta(days=1)

    features = _features_for_next_date(history, forecast_date)

    assert features.index[0] == forecast_date
    assert features.iloc[0]["day_of_week"] == forecast_date.dayofweek
    assert features.iloc[0]["day_of_month"] == forecast_date.day
    assert features.iloc[0]["month"] == forecast_date.month
    assert features.iloc[0]["is_weekend"] == int(forecast_date.dayofweek >= 5)
    assert features.iloc[0]["lag_1"] == history.iloc[-1]
    assert features.iloc[0]["lag_7"] == history.iloc[-7]
    assert features.iloc[0]["rolling_mean_7"] == pytest.approx(history.iloc[-7:].mean())
    assert features.notna().all().all()


def test_forecast_features_reject_a_date_already_in_history():
    dates = pd.date_range("2024-01-01", periods=35, freq="D")
    history = pd.Series([float(i + 1) for i in range(35)], index=dates)

    with pytest.raises(ForecastingDataError, match="must not already exist"):
        _features_for_next_date(history, dates[-1])


def test_ml_backtest_uses_rolling_origins_and_nonnegative_forecasts():
    values = [float(10 + (i % 7)) for i in range(100)]
    predictions, summary = walk_forward_ml_backtest(
        frame(values), product_id="P1", market="UK",
        horizon=7, min_train_days=56, step=7,
    )
    assert summary["backtest_origins"] > 0
    assert len(predictions) == summary["backtest_origins"] * 7
    assert predictions["ml_forecast"].ge(0).all()
    assert {"actual", "ml_forecast", "origin_date", "date"}.issubset(predictions.columns)


def test_ml_backtest_rejects_unknown_series():
    with pytest.raises(ForecastingDataError, match="No demand records"):
        walk_forward_ml_backtest(frame([1.0] * 80), product_id="missing", market="UK")


def test_ml_backtest_rejects_missing_dates_when_requested():
    data = frame([1.0] * 80).drop(index=5)
    with pytest.raises(ForecastingDataError, match="missing calendar dates"):
        walk_forward_ml_backtest(
            data, product_id="P1", market="UK", fill_missing_days_with_zero=False
        )
