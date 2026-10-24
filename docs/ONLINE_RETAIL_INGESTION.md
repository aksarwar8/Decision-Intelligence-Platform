# Online Retail Dataset Ingestion

## Purpose

The UCI Online Retail workbook is transaction-line data. It is not a ready-made
daily demand table. This module turns eligible sales lines into daily demand
observations suitable for exploratory analysis and a first forecasting baseline.

## Source schema

Required fields: `InvoiceNo`, `StockCode`, `Quantity`, `InvoiceDate`,
`UnitPrice`, and `Country`. `Description` is optional metadata.

## Transformation

The `prepare_daily_demand` function groups by:

- `date`: calendar day derived from `InvoiceDate`
- `product_id`: `StockCode`
- `market`: `Country` (the source has no store identifier)

It produces daily unit demand, line revenue, distinct invoice count, and a
product description. This is a demand aggregation, not a stock/inventory model.

## Data-quality policy

- Cancellation invoices whose invoice number starts with `C` are excluded.
- Rows with zero or negative quantity are excluded from the positive-sales
  demand target. These commonly represent returns or corrections and are
  reported in the quality summary.
- Invalid dates, nonnumeric quantities/prices, missing product identifiers, and
  negative prices are excluded and counted.
- Missing country values are retained under the `Unknown` market label.
- Invalid rows are summarized, but this first version does not persist each
  rejected source row to PostgreSQL.

## Limitations and next steps

1. The dataset has no store identifier, inventory level, promotion, or stockout
   data. Country is a market dimension, not a store.
2. It is historical (2010–2011) and must not be presented as live data.
3. Demand is based on positive sales only. Net sales/returns should be analyzed
   separately if needed.
4. Before forecasting, build a complete daily calendar per product/market and
   explicitly decide whether missing dates mean zero sales or missing data.
5. Use time-based backtesting and compare against naive and seasonal-naive
   baselines before selecting a more complex model.
6. The original PRD describes an M5 replay provider. This adapter is an
   alternative source and should not be confused with the M5 schema. Decide
   which source is the canonical V1 dataset before wiring this adapter into the
   existing replay API.
