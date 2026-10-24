"""Prepare the Online Retail workbook into daily demand CSV and quality JSON.

Usage from the repository root:
    python scripts/prepare_online_retail.py --input "data/Online Retail.xlsx"
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# Support running this file directly from the repository root.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.data.online_retail import load_online_retail, prepare_daily_demand  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/Online Retail.xlsx"),
        help="Path to the source Excel workbook",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/online_retail"),
        help="Directory for daily demand CSV and quality JSON",
    )
    args = parser.parse_args()

    try:
        raw = load_online_retail(args.input)
        daily, quality = prepare_daily_demand(raw)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "daily_demand.csv"
    report_path = args.output_dir / "quality_report.json"

    daily.to_csv(csv_path, index=False)
    report_path.write_text(
        json.dumps(quality, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Source rows: {quality['source_rows']:,}")
    print(f"Accepted sales rows: {quality['accepted_sales_rows']:,}")
    print(f"Daily demand rows: {quality['daily_demand_rows']:,}")
    print(f"Products: {quality['product_count']:,}")
    print(f"Markets: {quality['market_count']:,}")
    print(f"Date range: {quality['date_min']} to {quality['date_max']}")
    print(f"Daily data: {csv_path}")
    print(f"Quality report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
