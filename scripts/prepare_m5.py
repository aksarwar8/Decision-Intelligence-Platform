"""Prepare M5 data as the standard DecisionOS daily-demand CSV."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.data.m5 import load_m5_daily_demand  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sales", type=Path, default=Path("data/raw/m5/sales_train_validation.csv"))
    parser.add_argument("--calendar", type=Path, default=Path("data/raw/m5/calendar.csv"))
    parser.add_argument("--item-id", help="Optional M5 item_id filter")
    parser.add_argument("--store-id", help="Optional M5 store_id filter")
    parser.add_argument("--output", type=Path, default=Path("data/processed/m5/daily_demand.csv"))
    args = parser.parse_args()
    try:
        daily = load_m5_daily_demand(args.sales, args.calendar,
                                     item_id=args.item_id, store_id=args.store_id)
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(args.output, index=False)
    print(f"Wrote {len(daily):,} daily-demand rows to {args.output}")
    print(f"Products: {daily['product_id'].nunique():,}; stores: {daily['market'].nunique():,}")
    print(f"Date range: {daily['date'].min().date()} to {daily['date'].max().date()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
