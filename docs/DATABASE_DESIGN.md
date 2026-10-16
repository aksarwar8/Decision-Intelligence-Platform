# Decision Intelligence Platform

## Database Design Document

**Document Status:** Draft  
**Document Version:** 0.1  
**Product:** Decision Intelligence Platform  
**Initial Domain:** Indian Financial Market Intelligence  
**Database:** PostgreSQL  
**Related Documents:**

- `PRD.md`
- `SYSTEM_ARCHITECTURE.md`
- `TECHNOLOGY_DECISION_RECORDS.md`

---

# 1. Purpose

This document defines the database architecture and schema for the Decision Intelligence Platform.

The database must support:

- Market assets
- Historical market observations
- Data ingestion
- Data validation
- Prediction storage
- Model metadata
- Feature metadata
- Future MLOps requirements
- Data lineage
- Future expansion into other decision domains

The database design should remain simple enough for V1 while allowing the platform to evolve into a production-oriented system.

---

# 2. Database Objectives

The database should provide:

1. Persistent storage.
2. Data integrity.
3. Efficient historical-data retrieval.
4. Duplicate prevention.
5. Data lineage.
6. Prediction history.
7. Model traceability.
8. Support for incremental ingestion.
9. Clear relationships between entities.
10. Extensibility for future versions.

---

# 3. Database Technology

**Database:** PostgreSQL

PostgreSQL is selected because the V1 platform requires:

- Relational modeling
- SQL
- Constraints
- Transactions
- Indexing
- Referential integrity
- Production-oriented database experience

---

# 4. High-Level Entity Relationship

The initial database will contain the following major entities:

```text
                    ┌──────────────┐
                    │    assets    │
                    └──────┬───────┘
                           │
                           │ 1:N
                           ▼
                    ┌──────────────┐
                    │ market_data  │
                    └──────┬───────┘
                           │
                           │
                           ▼
                    ┌──────────────┐
                    │ predictions │
                    └──────┬───────┘
                           │
                           │ N:1
                           ▼
                    ┌──────────────┐
                    │    models    │
                    └──────────────┘


        ┌──────────────────────┐
        │   ingestion_runs     │
        └──────────┬───────────┘
                   │
                   ▼
          ingestion metadata


        ┌──────────────────────┐
        │   model_features     │
        └──────────┬───────────┘
                   │
                   ▼
             model metadata
```

The exact schema may evolve during implementation.

---

# 5. Core Tables

The initial schema will contain:

```text
assets
market_data
ingestion_runs
models
predictions
model_features
```

Additional tables will only be introduced when an actual requirement exists.

---

# 6. Table: assets

## Purpose

Stores information about financial assets supported by the platform.

Examples:

- Indian equities
- Market indices
- ETFs
- Other supported instruments

---

## Proposed Schema

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | BIGSERIAL | PRIMARY KEY | Internal asset identifier |
| symbol | VARCHAR(50) | NOT NULL, UNIQUE | Market symbol |
| name | VARCHAR(255) | NOT NULL | Asset name |
| exchange | VARCHAR(50) | NOT NULL | Exchange identifier |
| asset_type | VARCHAR(50) | NOT NULL | Equity, index, ETF, etc. |
| currency | VARCHAR(10) | NOT NULL | Currency |
| is_active | BOOLEAN | NOT NULL | Whether asset is active |
| created_at | TIMESTAMP | NOT NULL | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

---

## Example

```text
id: 1
symbol: RELIANCE
name: Reliance Industries
exchange: NSE
asset_type: EQUITY
currency: INR
is_active: true
```

The exact provider-specific symbol representation will be finalized after the market-data provider is selected.

---

# 7. Table: market_data

## Purpose

Stores validated historical market observations.

This is expected to become one of the largest tables in the system.

---

## Proposed Schema

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | BIGSERIAL | PRIMARY KEY | Internal record identifier |
| asset_id | BIGINT | FOREIGN KEY | Associated asset |
| timestamp | TIMESTAMP | NOT NULL | Market observation time |
| open | NUMERIC | NOT NULL | Opening price |
| high | NUMERIC | NOT NULL | Highest price |
| low | NUMERIC | NOT NULL | Lowest price |
| close | NUMERIC | NOT NULL | Closing price |
| volume | BIGINT | NOT NULL | Trading volume |
| source | VARCHAR(100) | NOT NULL | Data provider |
| created_at | TIMESTAMP | NOT NULL | Database insertion time |

---

# 8. Market Data Constraints

The database should enforce appropriate integrity rules.

Examples:

```text
high >= low
open > 0
high > 0
low > 0
close > 0
volume >= 0
```

The application-level validation layer will perform richer validation.

Database constraints provide an additional safety boundary.

---

# 9. Duplicate Prevention

A market observation should not be inserted more than once for the same asset and timestamp.

Therefore:

```text
UNIQUE(asset_id, timestamp)
```

should be considered a core database constraint.

Conceptually:

```text
Asset + Timestamp
       ↓
Unique Observation
```

This is particularly important for incremental ingestion.

---

# 10. Market Data Indexing

The most common queries are expected to be:

```text
Get market data for asset
Get recent observations
Get observations within date range
Get latest observation
```

Therefore an index should be created around:

```text
(asset_id, timestamp)
```

Potential query:

```sql
SELECT *
FROM market_data
WHERE asset_id = ?
ORDER BY timestamp DESC;
```

The exact indexing strategy will be validated against actual query performance.

---

# 11. Table: ingestion_runs

## Purpose

Records each attempt to retrieve external data.

This provides ingestion observability and data lineage.

---

## Proposed Schema

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Ingestion run identifier |
| source | VARCHAR(100) | Data provider |
| asset_id | BIGINT | Asset being ingested |
| ingestion_type | VARCHAR(50) | HISTORICAL / INCREMENTAL |
| started_at | TIMESTAMP | Start time |
| completed_at | TIMESTAMP | Completion time |
| status | VARCHAR(30) | SUCCESS / FAILED / PARTIAL |
| records_received | INTEGER | Number received |
| records_inserted | INTEGER | Number inserted |
| records_rejected | INTEGER | Number rejected |
| error_message | TEXT | Failure information |
| created_at | TIMESTAMP | Record creation time |

---

# 12. Ingestion Lifecycle

An ingestion run should follow:

```text
START
  ↓
Request External Data
  ↓
Receive Response
  ↓
Validate
  ↓
Transform
  ↓
Persist
  ↓
Record Statistics
  ↓
SUCCESS
```

If something fails:

```text
START
  ↓
External API
  ↓
FAILURE
  ↓
Log Error
  ↓
Record FAILED ingestion run
```

---

# 13. Why ingestion_runs Matters

Without ingestion metadata, it becomes difficult to answer questions such as:

- When was data last retrieved?
- Did ingestion succeed?
- How many records were received?
- How many records were rejected?
- Which provider supplied the data?
- Why is today's data missing?

This table therefore supports future monitoring and debugging.

---

# 14. Table: models

## Purpose

Stores metadata about trained ML models.

The actual serialized model artifact should not necessarily be stored directly inside PostgreSQL.

Instead, the database stores metadata and a reference to the artifact.

---

## Proposed Schema

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Model identifier |
| name | VARCHAR(255) | Model name |
| version | VARCHAR(100) | Model version |
| algorithm | VARCHAR(100) | Algorithm used |
| target | VARCHAR(255) | Prediction target |
| training_started_at | TIMESTAMP | Training start |
| training_completed_at | TIMESTAMP | Training completion |
| dataset_reference | TEXT | Dataset/version reference |
| feature_set_version | VARCHAR(100) | Feature version |
| artifact_uri | TEXT | Model artifact location |
| status | VARCHAR(50) | Candidate / Production / Archived |
| created_at | TIMESTAMP | Creation time |

---

# 15. Model Versioning

A model should be identifiable by a version.

Example:

```text
forecast_model
    │
    ├── v1
    ├── v2
    └── v3
```

A prediction should reference the exact model version that generated it.

This becomes increasingly important in V2 when MLflow is introduced.

---

# 16. Table: model_features

## Purpose

Stores metadata about the features used by a model.

---

## Proposed Schema

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Feature identifier |
| model_id | BIGINT | Associated model |
| feature_name | VARCHAR(255) | Feature name |
| feature_type | VARCHAR(50) | Numeric / categorical / temporal |
| transformation | TEXT | Transformation description |
| created_at | TIMESTAMP | Creation time |

---

# 17. Feature Versioning

Feature definitions may change over time.

For example:

```text
Feature Set V1
    ├── return_1d
    ├── return_5d
    └── volatility_20d


Feature Set V2
    ├── return_1d
    ├── return_5d
    ├── volatility_20d
    └── volume_change
```

Predictions should eventually be traceable to the feature version used to generate them.

---

# 18. Table: predictions

## Purpose

Stores model-generated predictions.

This allows the system to compare historical predictions with actual outcomes.

---

## Proposed Schema

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Prediction identifier |
| asset_id | BIGINT | Asset |
| model_id | BIGINT | Model used |
| prediction_timestamp | TIMESTAMP | Time prediction was generated |
| target_timestamp | TIMESTAMP | Future period being predicted |
| horizon | VARCHAR(50) | Forecast horizon |
| predicted_value | NUMERIC | Predicted value |
| lower_bound | NUMERIC | Lower prediction interval |
| upper_bound | NUMERIC | Upper prediction interval |
| actual_value | NUMERIC | Actual value when available |
| error | NUMERIC | Prediction error |
| created_at | TIMESTAMP | Record creation |

---

# 19. Prediction Lifecycle

Initially:

```text
Model
 ↓
Prediction
 ↓
Store Prediction
```

Later:

```text
Prediction
     ↓
Future Period
     ↓
Actual Value Arrives
     ↓
Calculate Error
     ↓
Store Error
```

This allows historical model evaluation.

---

# 20. Why Store Predictions?

Storing predictions allows the platform to answer:

- How accurate was the model?
- Which model version performed best?
- How does performance change over time?
- Did prediction error increase recently?
- Did the model perform poorly during volatile periods?

This becomes important for V2 monitoring.

---

# 21. Relationship Between Main Tables

The relationships are:

```text
assets
  │
  ├───────────────┐
  │               │
  ▼               ▼
market_data   predictions
                  │
                  ▼
                models
                  │
                  ▼
            model_features
```

And:

```text
assets
  │
  ▼
ingestion_runs
```

---

# 22. Foreign Keys

Expected relationships:

```text
market_data.asset_id
        ↓
assets.id
```

```text
ingestion_runs.asset_id
        ↓
assets.id
```

```text
predictions.asset_id
        ↓
assets.id
```

```text
predictions.model_id
        ↓
models.id
```

```text
model_features.model_id
        ↓
models.id
```

Foreign keys should be used to maintain referential integrity.

---

# 23. Complete Logical ER Diagram

```text
┌────────────────────────┐
│        assets          │
├────────────────────────┤
│ id PK                  │
│ symbol                 │
│ name                   │
│ exchange               │
│ asset_type             │
│ currency               │
│ is_active              │
│ created_at             │
│ updated_at             │
└───────────┬────────────┘
            │
       ┌────┴───────────────┐
       │                    │
       │                    │
       ▼                    ▼
┌──────────────────┐  ┌────────────────────┐
│   market_data    │  │   ingestion_runs   │
├──────────────────┤  ├────────────────────┤
│ id PK            │  │ id PK              │
│ asset_id FK      │  │ asset_id FK        │
│ timestamp        │  │ source             │
│ open             │  │ ingestion_type     │
│ high             │  │ started_at         │
│ low              │  │ completed_at       │
│ close            │  │ status             │
│ volume           │  │ records_received   │
│ source           │  │ records_inserted   │
│ created_at       │  │ records_rejected   │
└──────────────────┘  │ error_message      │
                      └────────────────────┘


┌────────────────────────┐
│        models          │
├────────────────────────┤
│ id PK                  │
│ name                   │
│ version                │
│ algorithm              │
│ target                 │
│ training_started_at    │
│ training_completed_at  │
│ dataset_reference      │
│ feature_set_version    │
│ artifact_uri           │
│ status                 │
│ created_at             │
└───────────┬────────────┘
            │
            │
       ┌────┴─────────────┐
       │                  │
       ▼                  ▼
┌─────────────────┐  ┌────────────────────┐
│ model_features  │  │    predictions     │
├─────────────────┤  ├────────────────────┤
│ id PK           │  │ id PK              │
│ model_id FK     │  │ asset_id FK        │
│ feature_name    │  │ model_id FK        │
│ feature_type    │  │ prediction_time    │
│ transformation  │  │ target_timestamp   │
│ created_at      │  │ horizon            │
└─────────────────┘  │ predicted_value    │
                     │ lower_bound        │
                     │ upper_bound        │
                     │ actual_value       │
                     │ error              │
                     │ created_at         │
                     └────────────────────┘
```

---

# 24. Data Lineage

The database should support the following lineage:

```text
External Provider
       ↓
Ingestion Run
       ↓
Market Data
       ↓
Feature Generation
       ↓
Model Version
       ↓
Prediction
```

Eventually:

```text
Prediction
    ↓
Explanation
    ↓
Retrieved Evidence
    ↓
LLM Response
```

The later stages will require additional schema design.

---

# 25. Raw Data Storage

Raw API responses may not belong directly inside the primary relational tables.

Potential approaches include:

### Option A — File/Object Storage

```text
Raw API Response
       ↓
JSON File
       ↓
Object Storage
```

### Option B — PostgreSQL JSONB

```text
Raw Response
       ↓
JSONB Column
```

### Decision

The exact raw-data storage mechanism is not finalized yet.

The decision will depend on:

- Data volume
- Provider response size
- Deployment environment
- Cost
- Reprocessing requirements

The relational schema should therefore not assume a specific raw-storage implementation yet.

---

# 26. Timestamp Strategy

The platform should use UTC internally wherever practical.

Market timestamps should preserve sufficient information to determine the original market observation time.

Conceptually:

```text
External Timestamp
       ↓
Normalize
       ↓
Internal Timestamp
```

The frontend may convert timestamps to the user's local timezone for display.

---

# 27. Numeric Precision

Financial prices should not be stored using floating-point database types when exact decimal representation is required.

PostgreSQL `NUMERIC` should be considered for:

- Prices
- Prediction values
- Prediction intervals

This avoids unnecessary floating-point representation issues at the database layer.

---

# 28. Soft Deletion

For core market observations, deletion should generally be avoided.

Historical market data should be treated as important analytical evidence.

For entities such as assets, an `is_active` field may be preferable to physically deleting records.

Example:

```text
is_active = false
```

This preserves historical relationships.

---

# 29. Data Retention

V1 will not automatically delete historical market data.

Retention policies may be introduced later based on:

- Storage requirements
- Data-provider licensing
- Business requirements
- Deployment costs

Any deletion policy must consider whether historical data is required for model reproducibility.

---

# 30. Transaction Strategy

Operations that modify related records should use database transactions where appropriate.

Example ingestion:

```text
Begin Transaction
      ↓
Validate Records
      ↓
Insert / Update Market Data
      ↓
Update Ingestion Run
      ↓
Commit
```

If a critical operation fails:

```text
Rollback
```

The exact transaction boundaries will be determined during implementation.

---

# 31. Concurrency Considerations

The system should avoid duplicate ingestion when multiple ingestion jobs run simultaneously.

Potential mechanisms include:

- Unique constraints
- Transaction isolation
- Job locking
- Application-level scheduling controls

The unique `(asset_id, timestamp)` constraint provides an important database-level protection.

---

# 32. Query Patterns

The schema should support common queries such as:

### Latest Market Data

```text
Get latest observations for asset
```

### Historical Data

```text
Get all observations for asset between dates
```

### Prediction History

```text
Get previous predictions for asset
```

### Model Performance

```text
Compare predictions generated by model versions
```

### Ingestion Health

```text
Get latest ingestion status
```

### Data Freshness

```text
Get latest stored market timestamp
```

---

# 33. Example Query: Latest Observation

Conceptually:

```sql
SELECT *
FROM market_data
WHERE asset_id = :asset_id
ORDER BY timestamp DESC
LIMIT 1;
```

An appropriate index should make this query efficient.

---

# 34. Example Query: Historical Data

Conceptually:

```sql
SELECT *
FROM market_data
WHERE asset_id = :asset_id
  AND timestamp BETWEEN :start_time AND :end_time
ORDER BY timestamp ASC;
```

This will be a core query used by the ML and analytics pipeline.

---

# 35. Example Query: Latest Ingestion

Conceptually:

```sql
SELECT *
FROM ingestion_runs
WHERE asset_id = :asset_id
ORDER BY started_at DESC
LIMIT 1;
```

This supports the data-freshness component of the dashboard.

---

# 36. Database Migration Strategy

Database schema changes should be version controlled.

The project should eventually use a migration system rather than manually modifying production databases.

Potential approach:

```text
Migration 001
    ↓
Initial Schema

Migration 002
    ↓
New Table

Migration 003
    ↓
New Column
```

The exact migration tool will be selected during implementation.

---

# 37. Database Environment Strategy

The project should eventually have separate databases for:

```text
Development
Testing
Production
```

Development:

```text
Local PostgreSQL
```

Testing:

```text
Test Database
```

Production:

```text
Managed PostgreSQL / Cloud Database
```

The exact deployment strategy will be determined later.

---

# 38. Future V2 Database Extensions

V2 may introduce additional metadata for:

- MLflow experiment references
- Model deployment status
- Monitoring metrics
- Drift results
- Retraining runs

Conceptually:

```text
models
   │
   ├── experiments
   ├── deployments
   ├── monitoring
   └── retraining_runs
```

These should not be implemented in V1 unless required.

---

# 39. Future V3 Database Extensions

V3 may require tables such as:

```text
documents
document_chunks
embedding_metadata
retrieval_runs
llm_interactions
evaluation_results
```

Conceptually:

```text
Documents
    ↓
Chunks
    ↓
Embeddings
    ↓
Retrieval
    ↓
LLM Response
```

The exact schema will be designed when RAG implementation begins.

---

# 40. Future V4 Database Extensions

V4 may require records for:

- Agent runs
- Tool calls
- Agent decisions
- Workflow execution
- Tool results

Conceptually:

```text
Agent Run
    ↓
Tool Calls
    ↓
Tool Results
    ↓
Final Response
```

These will be designed only when agentic functionality is introduced.

---

# 41. Multi-Domain Extension

The database should eventually support domains beyond financial markets.

The current architecture can begin with:

```text
assets
market_data
predictions
```

Future domains may use domain-specific entities.

For example:

```text
Financial:
Asset → Market Data

Demand:
Product → Demand Data

Supply Chain:
Product / Location → Supply Data
```

Shared platform entities such as models, predictions, ingestion, and monitoring may eventually be generalized where appropriate.

This generalization should not be forced into V1 prematurely.

---

# 42. Database Security

Database credentials must not be hardcoded.

The application should obtain database configuration through environment-based configuration.

Example:

```text
DATABASE_URL
```

Database access should use a least-privilege approach in deployed environments.

The application should not use a database superuser for normal runtime operations.

---

# 43. Backup Strategy

Production deployment should eventually include database backups.

Potential strategy:

```text
PostgreSQL
    ↓
Automated Backup
    ↓
Remote Storage
```

Backup frequency and retention will depend on deployment requirements.

V1 local development does not require a production backup system.

---

# 44. Performance Strategy

V1 should optimize only after measuring actual performance.

Potential optimization techniques include:

- Indexing
- Query optimization
- Pagination
- Connection pooling
- Batch inserts
- Caching

Premature optimization should be avoided.

---

# 45. Database Design Principles

The database should follow these principles:

### Principle 1 — Integrity

Invalid relationships should be prevented.

### Principle 2 — Traceability

Important predictions should be traceable to models and assets.

### Principle 3 — Reproducibility

Historical information should not be unnecessarily deleted.

### Principle 4 — Simplicity

Avoid unnecessary tables.

### Principle 5 — Explicit Relationships

Use foreign keys where appropriate.

### Principle 6 — Performance Through Measurement

Add indexes based on actual query patterns.

### Principle 7 — Evolution

Allow the schema to evolve through migrations.

---

# 46. V1 Database Summary

The core V1 database is:

```text
┌──────────────┐
│    assets    │
└──────┬───────┘
       │
       ├───────────────┐
       │               │
       ▼               ▼
┌──────────────┐ ┌────────────────┐
│ market_data  │ │ ingestion_runs │
└──────┬───────┘ └────────────────┘
       │
       │
       ▼
┌──────────────┐
│  predictions │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    models    │
└──────┬───────┘
       │
       ▼
┌────────────────┐
│ model_features │
└────────────────┘
```

---

# 47. V1 Minimum Schema

The minimum implementation should begin with:

```text
assets
market_data
ingestion_runs
models
predictions
```

`model_features` may be introduced alongside the model pipeline if required.

The schema should not be expanded merely for future possibilities.

---

# 48. Current Status

**Database Design Version:** 0.1  
**Status:** Draft

Completed:

- Database objectives
- Core entities
- Asset schema
- Market-data schema
- Ingestion schema
- Model schema
- Prediction schema
- Feature metadata
- Relationships
- Foreign keys
- Indexing strategy
- Data lineage
- Timestamp strategy
- Numeric precision
- Transaction strategy
- Query patterns
- Migration direction
- Security direction
- Future V2/V3/V4 extensions

Pending:

- Exact SQL schema
- Migration framework
- Exact ORM / database-access technology
- Exact raw-data storage mechanism
- Production database deployment
- Performance benchmarking

Next design document:

> **API Specification Document**