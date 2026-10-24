"""Run a rolling-origin baseline comparison on prepared Online Retail data.

Examples:
    python scripts/backtest_online_retail.py
    python scripts/backtest_online_retail.py --product-id 85123A --market "United Kingdom"
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

import pandas as pd  # noqa: E402
from app.ml.baselines import walk_forward_baseline_backtest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/online_retail/daily_demand.csv"),
        help="Prepared daily demand CSV",
    )
    parser.add_argument("--product-id", help="StockCode to evaluate")
    parser.add_argument("--market", help="Country/market to evaluate")
    parser.add_argument("--horizon", type=int, default=7, help="Forecast horizon in days")
    parser.add_argument(
        "--min-train-days",
        type=int,
        default=28,
        help="Minimum history before the first forecast origin",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/online_retail/backtest"),
        help="Output directory for metrics and forecast rows",
    )
    parser.add_argument(
        "--keep-missing-as-error",
        action="store_true",
        help="Fail when dates are missing rather than assuming zero sales",
    )
    args = parser.parse_args()

    if not args.input.exists():
        parser.error(
            f"Prepared data not found: {args.input}. First run "
            "'python scripts/prepare_online_retail.py --input "data/Online Retail.xlsx"'."
        )

    data = pd.read_csv(args.input, parse_dates=["date"])
    if args.product_id is None or args.market is None:
        counts = (
            data.groupby(["product_id", "market"], dropna=False)
            .size()
            .sort_values(ascending=False)
        )
        if counts.empty:
            parser.error("Prepared daily demand file contains no rows")
        suggested_product, suggested_market = counts.index[0]
        product_id = str(args.product_id or suggested_product)
        market = str(args.market or suggested_market)
        print(
            "Selected the product/market with the most observed daily rows: "
            f"product_id={product_id!r}, market={market!r}. "
            "Pass --product-id and --market to choose another series."
        )
    else:
        product_id, market = str(args.product_id), str(args.market)

    try:
        predictions, summary = walk_forward_baseline_backtest(
            data,
            product_id=product_id,
            market=market,
            horizon=args.horizon,
            min_train_days=args.min_train_days,
            fill_missing_days_with_zero=not args.keep_missing_as_error,
        )
    except ValueError as exc:
        parser.error(str(exc))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = args.output_dir / "forecast_backtest.csv"
    summary_path = args.output_dir / "forecast_metrics.json"
    predictions.to_csv(predictions_path, index=False)
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    print(f"Forecast rows: {predictions_path}")
    print(f"Metrics: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
