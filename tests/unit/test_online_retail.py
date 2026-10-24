import pandas as pd
import pytest

from app.data.online_retail import (
    OnlineRetailDataError,
    load_online_retail,
    prepare_daily_demand,
)


def sample_transactions():
    return pd.DataFrame(
        [
            {
                "InvoiceNo": "1001",
                "StockCode": "P1",
                "Description": "Widget",
                "Quantity": 2,
                "InvoiceDate": "2011-01-01 10:00:00",
                "UnitPrice": 5.0,
                "CustomerID": 10,
                "Country": "United Kingdom",
            },
            {
                "InvoiceNo": "1002",
                "StockCode": "P1",
                "Description": "Widget",
                "Quantity": 3,
                "InvoiceDate": "2011-01-01 12:00:00",
                "UnitPrice": 5.0,
                "CustomerID": 11,
                "Country": "United Kingdom",
            },
            {
                "InvoiceNo": "1003",
                "StockCode": "P2",
                "Description": "Gadget",
                "Quantity": 4,
                "InvoiceDate": "2011-01-02 09:00:00",
                "UnitPrice": 2.5,
                "CustomerID": 12,
                "Country": "France",
            },
            {
                "InvoiceNo": "C1004",
                "StockCode": "P1",
                "Description": "Widget",
                "Quantity": -2,
                "InvoiceDate": "2011-01-02 10:00:00",
                "UnitPrice": 5.0,
                "CustomerID": 10,
                "Country": "United Kingdom",
            },
            {
                "InvoiceNo": "1005",
                "StockCode": "P1",
                "Description": "Widget",
                "Quantity": -1,
                "InvoiceDate": "2011-01-03 10:00:00",
                "UnitPrice": 5.0,
                "CustomerID": 10,
                "Country": "United Kingdom",
            },
        ]
    )


def test_daily_demand_aggregates_sales_by_date_product_and_market():
    daily, quality = prepare_daily_demand(sample_transactions())

    row = daily.loc[
        (daily["date"] == pd.Timestamp("2011-01-01"))
        & (daily["product_id"] == "P1")
        & (daily["market"] == "United Kingdom")
    ].iloc[0]

    assert row["demand"] == 5
    assert row["revenue"] == 25.0
    assert row["transaction_count"] == 2
    assert quality["source_rows"] == 5
    assert quality["accepted_sales_rows"] == 3
    assert quality["daily_demand_rows"] == 2
    assert quality["total_units_sold"] == 9.0


def test_cancellations_and_nonpositive_quantities_are_not_forecast_demand():
    daily, quality = prepare_daily_demand(sample_transactions())

    assert daily["demand"].sum() == 9
    assert quality["cancellation_invoices"] == 1
    assert quality["nonpositive_quantity_rows"] == 2


def test_missing_required_columns_raise_actionable_error():
    with pytest.raises(OnlineRetailDataError, match="missing required columns"):
        prepare_daily_demand(pd.DataFrame({"InvoiceNo": ["1"]}))


def test_empty_input_is_rejected():
    columns = [
        "InvoiceNo", "StockCode", "Quantity", "InvoiceDate",
        "UnitPrice", "Country",
    ]
    with pytest.raises(OnlineRetailDataError, match="no transaction rows"):
        prepare_daily_demand(pd.DataFrame(columns=columns))


def test_no_usable_sales_rows_is_rejected():
    frame = sample_transactions().iloc[[3]].copy()
    with pytest.raises(OnlineRetailDataError, match="No valid positive sales rows"):
        prepare_daily_demand(frame)


def test_missing_workbook_path_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError, match="workbook not found"):
        load_online_retail(tmp_path / "missing.xlsx")
