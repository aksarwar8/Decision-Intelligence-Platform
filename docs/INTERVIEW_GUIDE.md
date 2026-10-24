# DecisionOS — Interview Guide

This guide describes the code that exists today. Be clear about what is implemented and what is planned.

## 1. A 30-second explanation

“DecisionOS is a retail demand forecasting and decision-support project. I chose the M5 Forecasting dataset as the canonical V1 source. I built a loader that converts the wide sales CSV and calendar mapping into a common daily-demand schema. The repository also contains baseline and feature-based ML walk-forward evaluation, a FastAPI ingestion API, SQLAlchemy models and Alembic migrations for daily demand and ingestion runs, and unit-test CI through GitHub Actions. The next step is validating replay-to-PostgreSQL locally, then serving forecasts through the API and building inventory-aware decisions.”

## 2. A 90-second architecture walkthrough

“Data comes from local M5 CSV files. The loader maps each M5 day ID to a date and normalizes the rows to date, product ID, market/store, and demand. The provider isolates M5-specific file handling from the rest of the application.

“The FastAPI route receives a request for one item/store series and coordinates the replay. The repository writes observations to PostgreSQL using SQLAlchemy. A unique key on date, product, and market is intended to prevent duplicates when a series is imported again. An ingestion-run record tracks provider, status, timestamps, and counts.

“Forecasting is kept separate from the API. Baseline and ML modules run walk-forward backtests, while scripts save predictions and metrics. GitHub Actions automatically runs unit tests when code changes.

“The components and CI exist, but I still need to validate the full ingestion flow against the actual local M5 files and PostgreSQL. Forecast serving, inventory recommendations, dashboard, RAG, and agent workflows are future stages rather than completed features.”

## 3. Explain the main components

| Component | Simple explanation |
|---|---|
| FastAPI route | Entry point for an HTTP request; validates input and calls the right code. |
| Provider | Knows how to read a particular source, currently local M5 CSV files. |
| Data loader | Converts the raw source format into clean, consistent daily rows. |
| Schema | Defines the shape of valid requests or responses. |
| Repository | Owns database queries and persistence. |
| SQLAlchemy model | Maps a Python class to a database table. |
| Alembic migration | Versions database structure changes so they can be applied repeatably. |
| Ingestion run | Audit record for one attempt to load data. |
| Baseline | Simple forecast used as a reference for a more complex model. |
| Walk-forward backtest | Uses past observations to predict the next window, moves forward, and repeats. |
| GitHub Actions | Automatically runs the unit-test suite on code changes. |

## 4. Likely interview questions

**Why M5?**  
“M5 is a retail forecasting benchmark with item/store sales and a calendar mapping. It is suitable for building demand-forecasting workflows. It does not provide current on-hand inventory, open orders, supplier lead times, or replenishment costs, so I cannot claim real inventory optimization from M5 alone.”

**Why normalize the data?**  
“The raw M5 sales table is wide, with a separate column for each day. Storage and forecasting are easier with one row per date, product, and store. A canonical schema also reduces dependence on the original provider format.”

**Why a provider interface?**  
“It separates source-specific parsing from application logic. A future provider can follow the same contract without rewriting the forecasting module. M5 is the current implementation; a live provider is future work.”

**Why PostgreSQL and SQLAlchemy?**  
“PostgreSQL stores persistent demand observations and ingestion metadata. SQLAlchemy maps database tables to Python models and handles queries, while repositories centralize persistence. Alembic versions schema changes.”

**How do you avoid duplicate observations?**  
“The daily-demand table has a unique key on date, product ID, and market. The repository updates an existing observation or inserts a new one. I still need to verify this behaviour against the actual local PostgreSQL setup with an integration test.”

**How do you evaluate forecasts?**  
“I compare simple baselines, such as last-value and weekly seasonal-naive, against a feature-based ML model. Walk-forward evaluation preserves temporal order. I review MAE, RMSE, and WAPE on comparable forecast windows. I claim improvement only if measured results support it.”

**Is it a live production platform?**  
“No. It uses local historical M5 data. The replay endpoint handles a bounded historical ingestion request; it is not a live retail data feed.”

**Does it recommend order quantities already?**  
“Not yet. That requires on-hand stock, open purchase orders, lead times, and explicit safety-stock or service-level rules. A demand forecast alone is insufficient.”

**Is RAG already integrated?**  
“No. RAG is a planned layer for answering questions from retrieved operational documents and explaining results with evidence.”

**What is the next milestone?**  
“Verify M5 replay against local PostgreSQL, add endpoint-level integration tests, and record reproducible M5 backtest metrics before expanding the product.”

## 5. One sentence to remember

**“The API coordinates the workflow, the provider reads the source, the loader standardizes data, the repository persists it, and the ML module evaluates forecasts.”**
