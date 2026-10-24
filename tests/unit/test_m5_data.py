import pandas as pd
import pytest

from app.data.m5 import M5DataError, load_m5_daily_demand


def write_files(tmp_path, calendar=None, sales=None):
    sales_path, calendar_path = tmp_path / "sales.csv", tmp_path / "calendar.csv"
    if sales is None:
        sales = pd.DataFrame([
            {"item_id": "ITEM_1", "store_id": "STORE_1", "d_1": 2, "d_2": 0},
            {"item_id": "ITEM_2", "store_id": "STORE_1", "d_1": 5, "d_2": 3},
            {"item_id": "ITEM_1", "store_id": "STORE_2", "d_1": 7, "d_2": 4},
        ])
    if calendar is None:
        calendar = pd.DataFrame({"d": ["d_1", "d_2"], "date": ["2016-01-01", "2016-01-02"]})
    sales.to_csv(sales_path, index=False)
    calendar.to_csv(calendar_path, index=False)
    return sales_path, calendar_path


def test_loader_maps_day_ids_filters_series_and_keeps_zero_days(tmp_path):
    sales, calendar = write_files(tmp_path)
    daily = load_m5_daily_demand(sales, calendar, item_id="ITEM_1", store_id="STORE_1")
    assert list(daily.columns) == ["date", "product_id", "market", "demand"]
    assert daily["date"].tolist() == [pd.Timestamp("2016-01-01"), pd.Timestamp("2016-01-02")]
    assert daily["demand"].tolist() == [2.0, 0.0]
    assert set(daily["market"]) == {"STORE_1"}


def test_loader_rejects_unknown_series(tmp_path):
    sales, calendar = write_files(tmp_path)
    with pytest.raises(M5DataError, match="No M5 rows found"):
        load_m5_daily_demand(sales, calendar, item_id="MISSING")


def test_loader_rejects_calendar_missing_day_ids(tmp_path):
    sales, calendar = write_files(
        tmp_path, calendar=pd.DataFrame({"d": ["d_1"], "date": ["2016-01-01"]})
    )
    with pytest.raises(M5DataError, match="missing sales day IDs"):
        load_m5_daily_demand(sales, calendar)


def test_loader_rejects_negative_sales(tmp_path):
    sales, calendar = write_files(
        tmp_path, sales=pd.DataFrame([{"item_id": "ITEM_1", "store_id": "STORE_1", "d_1": -1}])
    )
    with pytest.raises(M5DataError, match="cannot be negative"):
        load_m5_daily_demand(sales, calendar)
