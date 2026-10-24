from pathlib import Path

import pandas as pd

from scripts.backtest_demand import main


def test_backtest_cli_reports_missing_input_without_running_models(tmp_path):
    try:
        main(["--input", str(tmp_path / "missing.csv")])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected argparse to reject a missing input file")


def test_backtest_cli_rejects_missing_schema(tmp_path):
    path = tmp_path / "demand.csv"
    pd.DataFrame({"date": ["2020-01-01"], "demand": [1]}).to_csv(path, index=False)
    try:
        main(["--input", str(path)])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected argparse to reject missing schema columns")
