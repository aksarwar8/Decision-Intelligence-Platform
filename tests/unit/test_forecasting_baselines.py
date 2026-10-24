import pandas as pd
import pytest

from app.ml.baselines import ForecastingDataError, walk_forward_baseline_backtest


def daily_frame(values, start="2024-01-01", product="P1", market="UK"):
    dates = pd.date_range(start, periods=len(values), freq="D")
    return pd.DataFrame({
        "date": dates,
        "product_id": product,
        "market": market,
        "demand": values,
    })


def test_walk_forward_backtest_returns_both_baselines():
    frame = daily_frame([1, 2, 3, 4, 5, 6, 7] * 8)
    predictions, summary = walk_forward_baseline_backtest(
        frame,
        product_id="P1",
        market="UK",
        horizon=7,
        min_train_days=28,
    )

    assert summary["backtest_origins"] == 4
    assert summary["forecasted_observations"] == 28
    assert set(["actual", "naive_forecast", "seasonal_naive_forecast"]).issubset(
        predictions.columns
    )
    assert summary["seasonal_naive"]["mae"] == 0
    assert summary["seasonal_naive"]["rmse"] == 0


def test_missing_dates_require_explicit_policy_when_zero_fill_disabled():
    frame = daily_frame([1] * 40).drop(index=5)
    with pytest.raises(ForecastingDataError, match="missing calendar dates"):
        walk_forward_baseline_backtest(
            frame,
            product_id="P1",
            market="UK",
            min_train_days=28,
            fill_missing_days_with_zero=False,
        )


def test_insufficient_history_is_reported():
    frame = daily_frame([2] * 30)
    with pytest.raises(ForecastingDataError, match="Need at least"):
        walk_forward_baseline_backtest(
            frame,
            product_id="P1",
            market="UK",
            horizon=7,
            min_train_days=28,
        )


def test_unknown_product_market_is_reported():
    frame = daily_frame([1] * 50)
    with pytest.raises(ForecastingDataError, match="No demand records"):
        walk_forward_baseline_backtest(
            frame,
            product_id="not-here",
            market="UK",
        )


def test_forecasts_use_only_data_before_each_origin():
    frame = daily_frame([1] * 35 + [999] * 7)
    predictions, _ = walk_forward_baseline_backtest(
        frame,
        product_id="P1",
        market="UK",
        horizon=7,
        min_train_days=28,
        step=7,
    )
    first_origin = predictions.loc[predictions["origin_date"] == "2024-01-28"]
    assert first_origin["naive_forecast"].eq(1).all()
    assert first_origin["seasonal_naive_forecast"].eq(1).all()
