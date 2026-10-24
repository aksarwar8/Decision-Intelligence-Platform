# Decision Intelligence Platform

A portfolio project exploring a reproducible decision-support workflow: ingest business data, validate it, forecast demand, evaluate forecasts against simple baselines, and expose results through a future API and dashboard.

> **Current scope:** the Online Retail ingestion and forecasting work is an experimental data/ML workflow. It is not yet integrated into the production API, dashboard, or a complete decision recommendation engine. The existing project configuration also references an M5 replay provider; choose and document the canonical V1 data source before integration.

## Current capabilities

- Load the UCI Online Retail Excel workbook and validate the required fields.
- Exclude cancellations/returns and invalid sales rows for the current demand target.
- Aggregate sales into daily demand by product and country/market.
- Write a data-quality report and a processed daily-demand CSV.
- Evaluate naive and weekly seasonal-naive baselines using rolling-origin backtesting.
- Evaluate a scikit-learn HistGradientBoostingRegressor with lag, rolling-statistic, and calendar features.
- Report MAE, RMSE, and WAPE for the evaluated series.

## Repository areas

- `backend/app/data/online_retail.py` — workbook validation and daily demand aggregation.
- `backend/app/ml/baselines.py` — baseline forecasts and evaluation metrics.
- `backend/app/ml/forecasting.py` — feature-based ML forecasting and recursive walk-forward evaluation.
- `scripts/prepare_online_retail.py` — data preparation CLI.
- `scripts/backtest_online_retail.py` — baseline-versus-ML evaluation CLI.
- `tests/unit/` — unit tests for ingestion and forecasting.
- `docs/` — data assumptions and modeling documentation.

## Setup (PowerShell)

Run these commands from the repository root, with your virtual environment activated:

```powershell
pip install -r requirements.txt
$env:PYTHONPATH = "backend"
pytest tests/unit -v
```

Place the workbook at `data/Online Retail.xlsx`. The raw dataset is intentionally not expected to be committed to Git.

Prepare the data:

```powershell
python scripts/prepare_online_retail.py --input "data/Online Retail.xlsx"
```

Run the backtest:

```powershell
python scripts/backtest_online_retail.py
```

By default, the script selects the product-market combination with the most observed daily rows, uses a 7-day forecast horizon, 56 minimum training days, and 7 days between forecast origins. You can specify a series explicitly:

```powershell
python scripts/backtest_online_retail.py --product-id "85123A" --market "United Kingdom"
```

Results are written under `data/processed/online_retail/backtest/`, including baseline and ML prediction CSVs and metric JSON files.

## How to interpret results

- **MAE** is the mean absolute error in demand units.
- **RMSE** penalizes larger errors more strongly.
- **WAPE** expresses total absolute error relative to total actual demand; it can be unstable or uninformative when total actual demand is very small.
- Compare models only when they use the same forecast origins, dates, horizon, target definition, and missing-date policy.
- A backtest result on one product-market series is not evidence that the model generalizes across all products or markets.

### Data and modeling caveats

The workflow fills missing calendar dates with zero by default. In transaction data, a missing date can mean no recorded sales, but it can also mean incomplete reporting or a product not being offered. Validate this assumption for each use case. The current backtest evaluates one selected series by default; evaluate multiple representative series and report aggregate results before making broad performance claims. The ML forecasts are recursive, so later days in a forecast horizon use earlier model predictions as lag inputs.

## Configuration and secrets

Copy `.env.example` to a local `.env` and set your own local values. Never commit a real database password, API key, token, or other secret. If a real credential has ever been committed, rotate it; removing it from the current file does not remove it from Git history.

## Next steps

1. Validate the data-source decision (Online Retail versus the existing M5 replay configuration).
2. Run the unit suite and full backtest locally and record reproducible results.
3. Evaluate more product-market series and compare aggregate performance with the baselines.
4. Integrate a validated forecasting interface into the API, then add monitoring and a dashboard.
5. Add end-to-end tests and CI checks before treating results as release-ready.
