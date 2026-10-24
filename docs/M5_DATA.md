# M5 data workflow (DecisionOS V1)

M5 is the canonical V1 dataset. The files are historical retail data, not a live
inventory feed. Raw data should remain outside Git.

## Expected files

Place the official M5 CSV files under data/raw/m5/:

- sales_train_validation.csv
- calendar.csv

Each sales row is an item/store combination and each d_N column is daily unit
sales. The calendar maps day IDs to dates. The loader maps item_id to
product_id and store_id to market, producing the standard columns:
date, product_id, market, demand.

## Prepare a manageable subset

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "backend"
python scripts/prepare_m5.py --item-id "HOBBIES_1_001" --store-id "CA_1"
```

This writes data/processed/m5/daily_demand.csv. Filters are optional, but
recommended for local experiments because reshaping all M5 rows can use
substantial memory. Use IDs that exist in your downloaded files.

## Forecast evaluation

The output is compatible with the current evaluators. For example:

```powershell
python scripts/backtest_online_retail.py --input "data/processed/m5/daily_demand.csv" --product-id "HOBBIES_1_001" --market "CA_1" --output-dir "data/processed/m5/backtest"
```

The backtest script still has an Online Retail-specific name; a generic
forecast-evaluation CLI is a follow-up task.

## Limitations

- This first loader uses sales_train_validation.csv and calendar.csv only; it
  does not yet use sell_prices.csv, event features, or M5 evaluation rows.
- M5 provides sales, not current on-hand stock, purchase orders, supplier lead
  times, or replenishment costs. Those are needed for real inventory advice.
- Zero-sales days are retained.
- Tests use small synthetic CSV fixtures, not the full M5 download.
