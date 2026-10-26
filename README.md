# Decision Intelligence Platform

DecisionOS is a portfolio project for retail demand forecasting and operational decision support. The V1 canonical dataset is **M5 Forecasting**.

> **Current status:** M5 data preparation, forecasting/backtesting modules, an ingestion API/database foundation, and a first Streamlit dashboard are present. The dashboard expects a prepared daily-demand CSV. Validate the complete flow locally against your M5 files and PostgreSQL before describing it as end-to-end verified. Inventory recommendations remain future work.

## Current capabilities

- Load M5 item/store daily sales and map M5 day IDs to calendar dates.
- Filter an item/store subset before reshaping the wide M5 table.
- Produce the common demand schema: date, product_id, market, demand.
- Evaluate last-value and weekly seasonal-naive baselines plus a feature-based ML benchmark.
- Explore historical demand and compare forecast metrics in a Streamlit dashboard.
- Run unit tests locally and through GitHub Actions.

## Setup (PowerShell)

Run from the repository root with your virtual environment activated:

```powershell
pip install -r requirements.txt
$env:PYTHONPATH = "backend"
pytest tests/unit -v
```

## M5 data preparation

Download the M5 dataset files and place these two CSVs in `data/raw/m5/`:

- `sales_train_validation.csv`
- `calendar.csv`

Raw data should not be committed to Git. Prepare a single item/store series (use IDs that exist in your files):

```powershell
python scripts/prepare_m5.py --item-id "HOBBIES_1_001" --store-id "CA_1"
```

Output defaults to `data/processed/m5/daily_demand.csv`. Filters can be omitted, but reshaping the entire M5 table may consume substantial memory.

## Run the Streamlit dashboard

After preparing the CSV, run:

```powershell
streamlit run dashboard/streamlit_app.py
```

The dashboard lets you select a product/store, inspect historical demand, and run rolling-origin comparisons for a last-value baseline, weekly seasonal-naive baseline, and HistGradientBoosting model. The first evaluation can take some time because the ML model is refit at each backtest origin. You can change the prepared CSV path in the sidebar.

The dashboard reports MAE, RMSE and WAPE and allows prediction CSVs to be downloaded. Compare models on the same forecast horizon and origins. The result describes only the selected product/store series; it does not guarantee future performance.

## Run the backtest CLI

```powershell
python scripts/backtest_demand.py --input "data/processed/m5/daily_demand.csv" --product-id "HOBBIES_1_001" --market "CA_1" --output-dir "data/processed/m5/backtest"
```

The dataset-independent `scripts/backtest_demand.py` CLI evaluates any prepared CSV using the common demand schema. A successful unit-test run does not substitute for running and reviewing a full M5 backtest locally.

## M5 replay into PostgreSQL

Set `M5_DATA_DIRECTORY` to the directory containing `sales_train_validation.csv` and `calendar.csv` (defaults to `data/raw/m5`). Apply migrations with `alembic upgrade head`, start the API, then replay one item/store series:

```powershell
$env:PYTHONPATH = "backend"
alembic upgrade head
uvicorn app.main:app --reload --app-dir backend
```

Send a `POST` request to `/api/v1/ingestion/m5/replay` with JSON body `{"item_id":"HOBBIES_1_001","store_id":"CA_1"}`. The endpoint intentionally requires one item/store pair to limit memory use. Re-running the same series updates existing date/product/market keys instead of duplicating them. Raw M5 files remain local and must not be committed.

## Evaluation interpretation

- **MAE:** average absolute error in demand units.
- **RMSE:** penalizes larger errors more strongly.
- **WAPE:** total absolute error divided by total actual demand; interpret cautiously when total actual demand is very small.
- Compare models on identical forecast origins, dates, horizon, target definition, and missing-date policy.
- One item/store series is not evidence of generalization across all products and stores.

## Known limitations

- The M5 loader reads sales history and calendar dates; it does not yet use sell prices, event features, or the M5 evaluation rows.
- M5 contains sales, not current on-hand inventory, purchase orders, supplier lead times, or replenishment costs. Real replenishment recommendations need those inputs.
- Missing calendar dates are handled by the forecasting layer according to its configured policy; zero sales and unavailable data must not be confused.
- The M5 unit tests use small synthetic fixtures. The full raw dataset is not included in CI.
- The M5 replay-to-PostgreSQL path still needs a local run against your PostgreSQL database and real M5 files; GitHub CI uses synthetic fixtures, not the full dataset.
- The dashboard reads the prepared CSV directly; it is not yet connected to the PostgreSQL/API layer.
- Streamlit forecasting metrics are calculated on demand for one selected product/store, not precomputed for the entire dataset.

Start with the [system architecture](docs/SYSTEM_ARCHITECTURE.md) and [interview guide](docs/INTERVIEW_GUIDE.md). For details, see [M5 data workflow](docs/M5_DATA.md), [forecasting baselines](docs/FORECASTING_BASELINES.md), and [ML forecasting](docs/ML_FORECASTING.md).

## Configuration and secrets

Copy `.env.example` to a local `.env` and set your own values. Never commit real passwords, API keys, tokens, or other secrets. If a real credential has been committed, rotate it; removing it from the current file does not remove it from Git history.

## Next milestones

1. Run the M5 preparation and dashboard locally and record reproducible metrics.
2. Verify M5 replay into PostgreSQL and add endpoint-level integration tests.
3. Add sell-price/event features only with a time-aware leakage policy.
4. Add inventory data and explicitly sourced assumptions before implementing replenishment recommendations.
5. Connect dashboard reads to the API/database and add end-to-end tests.
