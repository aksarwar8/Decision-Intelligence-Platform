# Feature-based ML forecasting

The Online Retail backtest now supports a first machine-learning model in addition to the naive and weekly seasonal-naive baselines.

## Model

`HistGradientBoostingRegressor` from scikit-learn is trained separately at each rolling forecast origin. Features include demand lags (1, 2, 3, 7, 14 and 28 days), trailing rolling means and standard deviations (7, 14 and 28 days), and known calendar features (day of week, day of month, month and weekend flag).

The model produces a recursive multi-step forecast: for each next day, it predicts demand and uses that prediction to construct the following day's lag features. Predicted demand is clipped at zero because this target represents non-negative sales demand.

## Run locally

From the repository root, activate your virtual environment and run:

```powershell
pip install -r requirements.txt
$env:PYTHONPATH = "backend"
pytest tests/unit/test_online_retail.py tests/unit/test_forecasting_baselines.py tests/unit/test_forecasting_ml.py -v
python scripts/backtest_online_retail.py
```

The script writes:
- `forecast_backtest.csv` and `forecast_metrics.json` for the baseline comparison.
- `ml_forecast_backtest.csv` and `ml_forecast_metrics.json` for the ML model.

## Evaluation caveats

- Baselines and ML use the same minimum training history, forecast horizon, and rolling step so forecast windows can be aligned.
- Missing calendar dates are filled with zero by default. This is an explicit assumption, not proof that the product had zero demand on those dates. Use `--keep-missing-as-error` to reject incomplete calendars.
- Evaluate additional product/market series before drawing conclusions about generalization.
- This model is a first benchmark, not a production-ready replenishment policy. Inventory decisions also need lead times, stock on hand, costs, and service-level targets.
