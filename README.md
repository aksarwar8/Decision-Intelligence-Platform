# Decision Intelligence Platform

DecisionOS is a portfolio project for retail demand forecasting and operational decision support. The V1 canonical dataset is **M5 Forecasting**.

> **Current status:** the M5 CSV loader and preparation CLI are implemented with unit tests. The data workflow is not yet integrated with the production API, PostgreSQL ingestion, inventory recommendations, or dashboard. No full-dataset backtest has been claimed.

## Current capabilities

- Load M5 item/store daily sales and map M5 day IDs to calendar dates.
- Filter an item/store subset before reshaping the wide M5 table.
- Produce the common demand schema: date, product_id, market, demand.
- Evaluate naive and weekly seasonal-naive baselines and a feature-based ML benchmark using the existing evaluation modules.
- Run unit tests locally and through GitHub Actions.

## Setup (PowerShell)

Run from the repository root with your virtual environment activated:

```powershell
pip install -r requirements.txt
$env:PYTHONPATH = "backend"
pytest tests/unit -v
```

## M5 data preparation

Download the official M5 dataset files and place these two CSVs in `data/raw/m5/`:

- `sales_train_validation.csv`
- `calendar.csv`

Raw data should not be committed to Git. Prepare a single item/store series (use IDs that exist in your files):

```powershell
python scripts/prepare_m5.py --item-id "HOBBIES_1_001" --store-id "CA_1"
```

Output defaults to `data/processed/m5/daily_demand.csv`. Filters can be omitted, but reshaping the entire M5 table may consume substantial memory.

To evaluate the prepared series with the existing backtest CLI:

```powershell
python scripts/backtest_demand.py --input "data/processed/m5/daily_demand.csv" --product-id "HOBBIES_1_001" --market "CA_1" --output-dir "data/processed/m5/backtest"
```

The dataset-independent `scripts/backtest_demand.py` CLI evaluates any prepared CSV using the common demand schema. A successful unit-test run does not substitute for running and reviewing a full M5 backtest locally.

## Evaluation interpretation

- **MAE:** average absolute error in demand units.
- **RMSE:** penalizes larger errors more strongly.
- **WAPE:** total absolute error divided by total actual demand; interpret cautiously when total actual demand is very small.
- Compare models on identical forecast origins, dates, horizon, target definition, and missing-date policy.
- One item/store series is not evidence of generalization across all products and stores.

## Known limitations

- The first M5 loader reads sales history and calendar dates; it does not yet use sell prices, event features, or the M5 evaluation rows.
- M5 contains sales, not current on-hand inventory, purchase orders, supplier lead times, or replenishment costs. Real replenishment recommendations need those inputs.
- Missing calendar dates are handled by the forecasting layer according to its configured policy; zero sales and unavailable data must not be confused.
- The M5 unit tests use small synthetic fixtures. The full raw dataset is not included in CI.
- The ML workflow is not yet integrated into the API or persisted in PostgreSQL.

See [M5 data workflow](docs/M5_DATA.md), [forecasting baselines](docs/FORECASTING_BASELINES.md), and [ML forecasting](docs/ML_FORECASTING.md).

## Configuration and secrets

Copy `.env.example` to a local `.env` and set your own values. Never commit real passwords, API keys, tokens, or other secrets. If a real credential has been committed, rotate it; removing it from the current file does not remove it from Git history.

## Next milestones

1. Generalize the backtest CLI so its name and defaults are dataset-independent.
2. Run the M5 preparation and backtest locally on the downloaded dataset and record reproducible metrics.
3. Add sell-price/event features only with a time-aware leakage policy.
4. Implement the M5 replay-provider and database-ingestion path.
5. Add inventory data and explicitly sourced assumptions before implementing replenishment recommendations.
6. Integrate the validated forecasting interface into the API, then add end-to-end tests and dashboard support.
