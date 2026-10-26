
import pandas as pd
import pytest

from app.data.m5 import M5DataError, load_m5_daily_demand


def test_loader_reads_one_series(tmp_path):
    pd.DataFrame([
        {
            "item_id": "ITEM_1",
            "store_id": "STORE_1",
            "d_1": 3,
            "d_2": 0,
        }
    ]).to_csv(
        tmp_path / "sales_train_validation.csv",
        index=False,
    )

    pd.DataFrame({
        "d": ["d_1", "d_2"],
        "date": ["2016-01-01", "2016-01-02"],
    }).to_csv(tmp_path / "calendar.csv", index=False)

    result = load_m5_daily_demand(
        tmp_path / "sales_train_validation.csv",
        tmp_path / "calendar.csv",
        item_id="ITEM_1",
        store_id="STORE_1",
    )

    assert list(result.columns) == [
        "date", "product_id", "market", "demand"
    ]
    assert result["demand"].tolist() == [3.0, 0.0]


def test_loader_rejects_missing_series(tmp_path):
    pd.DataFrame([
        {"item_id": "ITEM_1", "store_id": "STORE_1", "d_1": 3}
    ]).to_csv(
        tmp_path / "sales_train_validation.csv",
        index=False,
    )

    pd.DataFrame({
        "d": ["d_1"],
        "date": ["2016-01-01"],
    }).to_csv(tmp_path / "calendar.csv", index=False)

    with pytest.raises(M5DataError, match="No M5 rows found"):
        load_m5_daily_demand(
            tmp_path / "sales_train_validation.csv",
            tmp_path / "calendar.csv",
            item_id="MISSING",
            store_id="STORE_1",
        )
