# Forecasting Baselines

## Why start with baselines?

A more complex model is not useful unless it improves on simple forecasts over
the same future dates. DecisionOS starts with:

- **Naive:** every day in the horizon equals the latest observed demand.
- **Seasonal naive:** repeats the most recent seven daily values, preserving a
  weekly pattern.

These are comparison points, not claims that either is the best production model.

## Evaluation design

`walk_forward_baseline_backtest` performs rolling-origin evaluation. At each
origin it trains/reads only the observations available before that origin and
forecasts the next horizon. It aggregates predictions from multiple origins and
reports:

- MAE: average absolute error, in units of demand
- RMSE: square-root mean squared error, in units of demand
- WAPE: total absolute error divided by total absolute actual demand, as a
  percentage; undefined when all evaluated actuals are zero

The script defaults to a 7-day horizon and 28 days of minimum history. These are
initial settings to validate, not tuned final values.

## Missing dates

Online Retail contains transaction events, not a complete daily panel. The CLI
defaults to filling missing dates with zero demand. This is an explicit
assumption: a missing date can mean no sales, but it can also mean unavailable
data. Use `--keep-missing-as-error` to stop when dates are absent, and decide
the policy before treating the metrics as business evidence.

## Run it

From the repository root, after installing dependencies and preparing the
workbook:

```powershell
$env:PYTHONPATH = "backend"
pytest tests/unit/test_forecasting_baselines.py -v
python scripts/backtest_online_retail.py
```

To evaluate a specific product and country:

```powershell
python scripts/backtest_online_retail.py --product-id "85123A" --market "United Kingdom"
```

Outputs are written to `data/processed/online_retail/backtest/`:

- `forecast_backtest.csv`: actuals and predictions at each origin
- `forecast_metrics.json`: aggregate metrics and evaluation metadata

Do not select a complex model until it is compared on identical rolling origins.
For a stronger experiment, add several origins, report results by series, and
compare against the same held-out dates.
