"""Run baseline and ML demand-forecast evaluations on prepared data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

import pandas as pd  # noqa: E402
from app.ml.baselines import walk_forward_baseline_backtest  # noqa: E402
from app.ml.forecasting import walk_forward_ml_backtest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/processed/online_retail/daily_demand.csv"))
    parser.add_argument("--product-id", help="StockCode to evaluate")
    parser.add_argument("--market", help="Country/market to evaluate")
    parser.add_argument("--horizon", type=int, default=7)
    parser.add_argument("--min-train-days", type=int, default=56)
    parser.add_argument("--step", type=int, default=7, help="Days between forecast origins")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/online_retail/backtest"))
    parser.add_argument("--keep-missing-as-error", action="store_true")
    args = parser.parse_args()

    if not args.input.exists():
        parser.error(
            f"Prepared data not found: {args.input}. "
            'First run: python scripts/prepare_online_retail.py --input "data/Online Retail.xlsx"'
        )

    data = pd.read_csv(args.input, parse_dates=["date"])
    counts = data.groupby(["product_id", "market"], dropna=False).size().sort_values(ascending=False)
    if counts.empty:
        parser.error("Prepared daily demand file contains no rows")
    product_id = str(args.product_id or counts.index[0][0])
    market = str(args.market or counts.index[0][1])
    print(f"Evaluating product_id={product_id!r}, market={market!r}")

    common = {
        "product_id": product_id,
        "market": market,
        "horizon": args.horizon,
        "step": args.step,
        "fill_missing_days_with_zero": not args.keep_missing_as_error,
    }
    try:
        # Use the same minimum history and step so the forecast windows align.
        baseline_predictions, baseline_summary = walk_forward_baseline_backtest(
            data, **common, min_train_days=args.min_train_days
        )
        ml_predictions, ml_summary = walk_forward_ml_backtest(
            data, **common, min_train_days=args.min_train_days
        )
    except ValueError as exc:
        parser.error(str(exc))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    baseline_predictions.to_csv(args.output_dir / "forecast_backtest.csv", index=False)
    (args.output_dir / "forecast_metrics.json").write_text(
        json.dumps(baseline_summary, indent=2) + "\n", encoding="utf-8"
    )
    ml_predictions.to_csv(args.output_dir / "ml_forecast_backtest.csv", index=False)
    (args.output_dir / "ml_forecast_metrics.json").write_text(
        json.dumps(ml_summary, indent=2) + "\n", encoding="utf-8"
    )
    print("Baseline metrics:")
    print(json.dumps(baseline_summary, indent=2))
    print("ML metrics:")
    print(json.dumps(ml_summary, indent=2))
    print(f"Outputs written to: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
