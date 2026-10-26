"""Tests for baseline and machine-learning forecasting entry points."""

import pandas as pd
import pytest

from app.ml.baselines import ForecastingDataError, walk_forward_baseline_backtest


def test_baseline_backtest_returns_forecasts():
    dates = pd.date_range("2024-01-01", periods=42, freq="D")
    data = pd.DataFrame({"date": dates, "product_id": "ITEM_1", "market": "STORE_1", "demand": [float(i % 7 + 1) for i in range(42)]})
    predictions, summary = walk_forward_baseline_backtest(data, product_id="ITEM_1", market="STORE_1", horizon=3, min_train_days=28)
    assert len(predictions) == 15
    assert summary["forecasted_observations"] == len(predictions)
    assert summary["naive"]["mae"] >= 0


def test_baseline_backtest_rejects_missing_columns():
    with pytest.raises(ForecastingDataError, match="missing required columns"):
        walk_forward_baseline_backtest(pd.DataFrame({"date": ["2024-01-01"]}), product_id="ITEM_1", market="STORE_1")
