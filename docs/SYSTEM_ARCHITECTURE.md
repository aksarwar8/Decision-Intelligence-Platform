# Decision Intelligence Platform

## System Architecture Document

**Document Status:** Draft  
**Document Version:** 0.2  
**Product:** Decision Intelligence Platform  
**Initial Domain:** Retail Demand Forecasting & Operational Intelligence  
**Initial Release:** V1  
**Related Document:** Product Requirements Document (PRD)

---

# 1. Purpose

This document defines the technical architecture of the Decision Intelligence Platform.

The architecture describes how the system will:

- Acquire data through an external-provider interface
- Replay historical data as incremental data availability
- Validate incoming data
- Store demand information
- Process and transform time-series data
- Generate analytical features
- Train and evaluate machine-learning models
- Generate demand forecasts
- Detect demand anomalies
- Serve predictions through an API
- Present results through a web application
- Support future MLOps, Explainable AI, RAG, and Agentic AI capabilities
- Support future expansion into additional decision-intelligence domains

The architecture will evolve incrementally across multiple versions.

The initial implementation will focus on V1.

---

# 2. Architecture Goals

The architecture should satisfy the following goals:

1. Separate data ingestion from machine learning.
2. Separate backend services from the frontend.
3. Maintain a clear boundary between raw data and validated data.
4. Make data providers replaceable.
5. Make ML models replaceable.
6. Support incremental data ingestion.
7. Support reproducible experiments and predictions.
8. Support time-aware machine-learning workflows.
9. Prevent temporal and future-data leakage.
10. Support automated testing.
11. Allow future MLOps integration.
12. Allow future RAG and LLM integration.
13. Allow future agentic workflows.
14. Allow the platform to support multiple domains in the future.
15. Avoid unnecessary infrastructure complexity.
16. Keep the system understandable and maintainable.

---

# 3. Architectural Principles

## 3.1 Separation of Concerns

Each major component should have one primary responsibility.

```text
Data Ingestion
      ↓
Data Validation
      ↓
Data Processing
      ↓
Feature Engineering
      ↓
Machine Learning
      ↓
Decision Support
      ↓
Backend API
      ↓
Frontend


3.2 Provider Independence

The ML and application layers should not directly depend on the M5 dataset or any specific future external data provider.

Instead, the platform should define an internal provider interface.

                  DemandDataProvider
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
      M5 Replay Provider      External API Provider
       (V1 / Simulation)          (Future)

This allows the provider to be changed without redesigning the rest of the platform.

The forecasting system should not need to know whether the data originated from a historical replay or a future live provider.

3.3 Model Independence

The application should not be tightly coupled to one ML algorithm.

The architecture should allow different models to be evaluated and replaced.

Forecasting Model Interface
          │
          ├── Naive Baseline
          ├── Seasonal Naive
          ├── Statistical Model
          ├── XGBoost
          ├── LightGBM
          └── Future Model
3.4 API-First Backend

The frontend should communicate with the backend through documented APIs.

The frontend should not directly access:

PostgreSQL
ML model files
Data-processing internals
External data-provider credentials

The backend controls access to these components.

3.5 Incremental Complexity

The architecture will evolve according to actual requirements.

We will not introduce technologies such as:

Kubernetes
Kafka
Microservices
Distributed processing
PySpark
Airflow
Databricks

unless a genuine requirement emerges.

The goal is to demonstrate depth and engineering understanding rather than simply collecting technologies.

3.6 Time-Series Integrity

Because V1 is a forecasting system, temporal ordering must be treated as a first-class architectural concern.

The system must ensure:

Past Information
      ↓
Feature Generation
      ↓
Prediction
      ↓
Future Actual

Future observations must never leak into features or training data for an earlier prediction.

4. High-Level Architecture

The overall V1 platform architecture is:

                    Historical Retail Dataset
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Replay Provider    │
                    │  M5 Historical Data │
                    └──────────┬──────────┘
                               │
                               │
                    Future External API
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Data Provider       │
                    │  Interface           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Data Ingestion     │
                    │  Service            │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Data Validation     │
                    │ & Data Quality      │
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
           Valid Data                Rejected Records
                  │                    / Error Store
                  ▼
             PostgreSQL
                  │
                  ▼
        ┌─────────────────────┐
        │ Data Processing &   │
        │ Feature Engineering │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Forecasting Engine  │
        │                     │
        │ Baselines           │
        │ XGBoost / LightGBM  │
        └──────────┬──────────┘
                   │
          ┌────────┴─────────┐
          ▼                  ▼
   ┌──────────────┐   ┌──────────────┐
   │ Evaluation   │   │   Anomaly    │
   │ & Backtesting│   │  Detection   │
   └──────┬───────┘   └──────┬───────┘
          │                  │
          └────────┬─────────┘
                   ▼
        ┌─────────────────────┐
        │ Decision Engine     │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │     FastAPI         │
        │     Backend         │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ React + TypeScript   │
        │ Dashboard            │
        └─────────────────────┘
5. System Layers

The system will be organized into the following conceptual layers:

┌──────────────────────────────────────────┐
│              Presentation                │
│          React + TypeScript              │
├──────────────────────────────────────────┤
│               API Layer                  │
│                FastAPI                   │
├──────────────────────────────────────────┤
│          Decision / ML Layer             │
│ Forecasting + Evaluation + Analytics     │
├──────────────────────────────────────────┤
│        Data Processing Layer             │
│ Cleaning + Features + Validation         │
├──────────────────────────────────────────┤
│              Data Layer                  │
│ PostgreSQL + Raw / Rejected Storage      │
├──────────────────────────────────────────┤
│            Ingestion Layer               │
│ Replay Provider + External API Provider  │
└──────────────────────────────────────────┘

Each layer should communicate through well-defined interfaces.

6. External Data Layer

The initial V1 system will use a public historical retail demand dataset such as an M5/Walmart-style dataset.

The dataset will provide information such as:

Product
Store
Date
Demand
Category
Department
Other available contextual attributes

The dataset is treated as historical data.

It should not be represented as a live production API.

The purpose of the initial dataset is to provide realistic time-series data while allowing the project to build a production-style ingestion architecture.

7. Demand Data Provider Interface

The ingestion layer should expose an internal provider abstraction.

Conceptually:

DemandDataProvider
│
├── get_historical_data()
├── get_latest_data()
└── get_metadata()

The V1 implementation will include:

DemandDataProvider
       │
       ├── M5ReplayProvider
       │
       └── ExternalAPIProvider
                         │
                         └── Future implementation

The concrete external API provider will be introduced only when a legitimate and suitable data source is selected.

8. Replay Provider Architecture

The M5 historical dataset will be exposed through a replay mechanism.

The replay provider simulates the behavior of an external source whose data becomes available incrementally over time.

Conceptually:

Historical Dataset
       ↓
Replay Clock
       ↓
Data Available Up To T
       ↓
Ingestion Service

For example:

Replay Clock = 2022-01-15

Available:
2022-01-01 → 2022-01-15

Unavailable:
2022-01-16 → Future

When the replay clock advances:

Replay Clock = 2022-01-16

Newly Available:
2022-01-16

This allows the entire downstream pipeline to behave as though new observations are continuously arriving.

9. Replay Provider Requirements

The replay provider should support:

Initial historical load
Incremental updates
Latest available timestamp
Duplicate simulation
Missing-data simulation
Malformed-record simulation
Provider failure simulation
Controlled replay speed
Reproducible replay runs
Replay reset

The replay provider must not simply expose the entire CSV file through an endpoint.

It should enforce temporal availability.

10. Replay API Architecture

A simple replay API may expose endpoints such as:

GET /replay/health

GET /replay/metadata

GET /replay/historical

GET /replay/incremental

POST /replay/advance

POST /replay/reset

The exact API design will be finalized during the API specification phase.

For example:

GET /replay/incremental?after=2022-01-14

may return only observations that became available after the specified timestamp.

11. Data Ingestion Architecture

The ingestion service is responsible for retrieving external or replayed data.

Its responsibilities include:

Provider communication
Request construction
Response parsing
Incremental data retrieval
Retry handling
Failure handling
Basic response validation
Data transformation
Ingestion logging

The ingestion service should not perform ML.

Conceptually:

Scheduler
    ↓
Provider
    ↓
Fetch New Data
    ↓
Parse
    ↓
Validate
    ↓
Persist
    ↓
Record Ingestion Metadata
12. Initial Historical Ingestion

When the platform is initialized:

Initial Dataset
      ↓
Replay Provider
      ↓
Historical Data
      ↓
Validation
      ↓
Transformation
      ↓
PostgreSQL

This creates the initial trusted historical dataset required for forecasting.

13. Incremental Ingestion

After the initial historical load, subsequent ingestion should retrieve only newly available observations.

Conceptually:

                    PostgreSQL
                        │
                        ▼
             Latest Stored Timestamp
                        │
                        ▼
                 Ingestion Service
                        │
                        ▼
                    Provider
                        │
                        ▼
                New Observations
                        │
                        ▼
                    Validation
                        │
                        ▼
                  Deduplication
                        │
                        ▼
                      UPSERT

The system should avoid unnecessarily downloading and storing duplicate observations.

14. Scheduler

The ingestion process should be triggered automatically.

Initial possibilities include:

Python scheduler
APScheduler
Cron
Scheduled CI execution

The scheduler should trigger:

Scheduler
    ↓
Ingestion
    ↓
Validation
    ↓
Storage

Airflow or another enterprise orchestration system may be introduced later if justified.

15. Data Validation Layer

The validation layer acts as a boundary between incoming data and trusted internal data.

Validation categories include:

Schema Validation
       +
Data Type Validation
       +
Missing Value Validation
       +
Duplicate Validation
       +
Temporal Validation
       +
Numerical Validation
       +
Business Rule Validation

Invalid data should not silently enter the ML pipeline.

Validation failures should be logged with enough information for debugging.

16. Data Quality Rules

Initial data-quality checks may include:

Required fields
Valid product IDs
Valid store IDs
Valid dates
Non-negative demand
Duplicate detection
Missing dates
Unexpected timestamp ordering
Invalid data types
Unexpected categorical values

The exact rules will be defined after examining the selected dataset.

17. Invalid Data Handling

The system should distinguish between:

Valid Data
     ↓
PostgreSQL

Invalid Data
     ↓
Rejected Records
     ↓
Validation Error Log

Each rejected record should have a reason.

Examples:

Missing product ID
Invalid store ID
Invalid date
Negative demand
Duplicate observation
Schema mismatch
Invalid data type
18. Raw Data Layer

Raw provider responses should be conceptually preserved separately from validated data where practical.

The raw layer provides:

Debugging capability
Reprocessing capability
Data lineage
Reproducibility
Provider-response inspection

Conceptual architecture:

Provider
   │
   ▼
Raw Response
   │
   ├──────────────► Raw Storage
   │
   ▼
Validation
   │
   ▼
Processed Data

The exact raw-storage implementation will be finalized during the database and technology design phases.

19. Processed Data Layer

Validated data will be transformed into the platform's internal demand representation.

Example:

Raw Provider Data
       ↓
Field Mapping
       ↓
Type Conversion
       ↓
Date Normalization
       ↓
Validation
       ↓
Internal Demand Schema

The internal schema should remain independent of provider-specific field names.

20. PostgreSQL

PostgreSQL will serve as the primary structured database in V1.

The database will store:

Products
Stores
Demand observations
Ingestion runs
Rejected records
Predictions
Model metadata
Evaluation results
Other application metadata

PostgreSQL provides persistent storage for both application and analytical workflows.

21. Database Access

Application components should not directly manipulate the database wherever possible.

The backend and dedicated data-access components should control database operations.

Conceptually:

React
  │
  ▼
FastAPI
  │
  ▼
Service Layer
  │
  ▼
Repository / Data Access
  │
  ▼
PostgreSQL

This keeps database logic separate from API and business logic.

22. Time-Series Data Model

The fundamental demand observation is:

Store
+
Product
+
Date
+
Demand

For example:

2022-01-15
Store A
Product X
Demand = 42

The system must preserve temporal ordering.

Rows must not be treated as independent observations when constructing forecasting datasets.

23. Data Processing Layer

The data-processing layer transforms validated observations into data suitable for analytics and machine learning.

Typical operations include:

Sorting
Missing-date handling
Cleaning
Type conversion
Time-index construction
Aggregation
Transformation
Feature generation

Conceptual flow:

Validated Demand Data
        ↓
Cleaning
        ↓
Temporal Processing
        ↓
Feature Engineering
        ↓
Model Dataset
24. Feature Engineering

Potential features include:

Lag Features
Lag 1
Lag 7
Lag 14
Other appropriate lags
Rolling Features
Rolling mean
Rolling median
Rolling standard deviation
Rolling minimum
Rolling maximum
Calendar Features
Day of week
Week of year
Month
Weekend indicator
Holiday/event indicators where available
Trend Features
Recent demand trend
Demand growth/change
Rolling trend statistics
Product / Store Features
Product category
Department
Store identifier
Other relevant categorical information

Features will be selected based on EDA and model experiments.

25. Temporal Leakage Prevention

The feature pipeline must prevent future information from entering historical training examples.

For example:

Prediction Time:
January 15

Allowed:
January 1 → January 15

Forbidden:
January 16 → Future

At every simulated prediction point:

The model may only use information that would have been available at that time.

This requirement is fundamental to the architecture.

26. Forecasting Pipeline

The ML pipeline will consist of:

Processed Data
      ↓
Feature Generation
      ↓
Temporal Split
      ↓
Baseline
      ↓
Model Training
      ↓
Validation
      ↓
Evaluation
      ↓
Model Selection
      ↓
Model Artifact

The initial ML implementation will use Python-based ML tooling.

Potential technologies include:

NumPy
Pandas
Scikit-learn
XGBoost
LightGBM

The final model selection will depend on experimentation.

27. Baseline Models

A baseline must be established before introducing complex ML models.

Possible baselines include:

Naive Forecast
Forecast = Most Recent Demand
Seasonal Naive
Forecast ≈ Demand from
the same period in the previous week
Moving Average

Uses recent historical demand.

Exponential Smoothing

May be evaluated as an additional statistical baseline.

The baseline provides the reference point for determining whether ML provides meaningful improvement.

28. Machine Learning Models

Feature-based ML models may include:

Random Forest
XGBoost
LightGBM

The initial preferred direction is a gradient-boosting model such as XGBoost or LightGBM.

Deep learning will not be introduced simply for complexity.

It should only be introduced if experimentation demonstrates that it provides meaningful value.

29. Time-Aware Training

The ML pipeline must preserve temporal ordering.

Example:

Historical Data
│
├───────────────┬──────────────┬─────────────┐
│               │              │
Training     Validation       Test
│               │              │
Past           Later          Future

Random shuffling should not be used when it would allow future information to influence training.

Potential validation approaches include:

Time-series split
Walk-forward validation
Expanding-window validation
30. Model Evaluation

Evaluation should include:

MAE
RMSE
MAPE where appropriate
Forecast bias
Baseline comparison
Error analysis

Evaluation should also examine:

Product-level performance
Store-level performance
Seasonal performance
High-demand periods
Low-demand periods

Where probabilistic forecasting is implemented:

Prediction interval coverage
Calibration-related analysis
31. Forecast Uncertainty

The system should not expose only a single predicted value.

Where feasible, forecasts should include an uncertainty range.

Example:

Expected Demand:
124 units

Prediction Range:
110 – 139 units

The exact prediction-interval methodology will be determined during implementation.

32. Prediction Persistence

Predictions should be stored so that they can later be compared against actual outcomes.

A prediction record should conceptually contain:

Prediction ID
Product ID
Store ID
Prediction Timestamp
Target Date
Predicted Value
Lower Bound
Upper Bound
Model ID
Model Version
Feature Version

When actual demand becomes available:

Prediction
     ↓
Actual Demand
     ↓
Forecast Error

This creates the foundation for future model monitoring.

33. Anomaly Detection

The platform should support basic demand anomaly detection.

Potential anomalies include:

Unusually high demand
Unusually low demand
Sudden demand changes
Missing observations
Unexpected patterns

Anomaly detection will initially support analysis rather than automatically making business decisions.

34. Decision Engine

The Decision Engine sits between analytics/ML and the API layer.

Its responsibility is to convert raw model outputs into structured decision-support information.

Example:

Model Output
     │
     ▼
Decision Engine
     │
     ├── Forecast
     ├── Forecast Range
     ├── Trend
     ├── Anomaly
     ├── Model Performance
     ├── Data Freshness
     └── Model Metadata

The Decision Engine should provide information for planning and analysis rather than blindly executing business decisions.

35. Decision-Oriented Output

The system should not only display:

Predicted Demand = 124

Instead, it should provide context such as:

Product:
A123

Store:
Store-01

Forecast Horizon:
Next 7 Days

Expected Demand:
124 units

Prediction Range:
110–139 units

Trend:
Increasing

Seasonality:
Weekend uplift detected

Recent Anomaly:
Demand unusually low

Model:
XGBoost v1

Baseline:
Seasonal Naive

Data Freshness:
Updated according to replay clock

This transforms the system from a simple forecasting model into a decision-intelligence system.

36. FastAPI Backend

FastAPI will expose platform capabilities through REST endpoints.

Conceptual architecture:

                    FastAPI
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
   Demand Data     Analytics       Forecast
       API             API            API

The backend will provide:

Request validation
Response schemas
Error handling
API documentation
Service orchestration
Future authentication
37. Backend Service Layer

The API layer should not contain all business logic.

Conceptually:

API Router
    ↓
Service Layer
    ↓
Domain Logic
    ↓
Repository / ML Components

Example:

GET /products
      ↓
Product Service
      ↓
Product Repository
      ↓
PostgreSQL

This separation improves testability and maintainability.

38. Initial API Capabilities

Potential endpoints include:

GET /health

GET /api/v1/products

GET /api/v1/stores

GET /api/v1/demand

GET /api/v1/demand/latest

GET /api/v1/data-freshness

GET /api/v1/ingestion/status

POST /api/v1/ingestion/run

GET /api/v1/forecasts

GET /api/v1/forecasts/{product_id}/{store_id}

GET /api/v1/predictions

GET /api/v1/models

GET /api/v1/models/{model_id}

GET /api/v1/models/{model_id}/performance

GET /api/v1/anomalies

The final API contract will be defined separately in:

docs/API_SPECIFICATION.md
39. Frontend Architecture

The frontend will use:

React + TypeScript

The frontend communicates with FastAPI.

React
  │
  │ HTTP / REST
  ▼
FastAPI
  │
  ▼
Decision Intelligence Services

The frontend should not contain:

ML logic
Feature-engineering logic
Database logic
Model-training logic
40. Dashboard Architecture

The V1 dashboard should contain components such as:

Dashboard
│
├── System Status
│
├── Data Freshness
│
├── Latest Ingestion Run
│
├── Product Selector
│
├── Store Selector
│
├── Historical Demand
│
├── Demand Forecast
│
├── Prediction Interval
│
├── Model Performance
│
├── Anomaly Detection
│
└── Data Quality

The exact UI design will be developed after the API contract is defined.

41. Authentication

Authentication is not required for the first local V1 prototype.

However, the architecture should allow authentication to be introduced later.

Potential future flow:

User
  ↓
Authentication
  ↓
Authorization
  ↓
API

Authentication should not be implemented prematurely if the V1 deployment does not require it.

42. Logging

The platform should maintain structured logs for important operations.

Examples:

Ingestion started
Provider request
Provider response
Validation started
Validation failure
Records inserted
Records rejected
Forecast generation started
Forecast generation completed
API request
Database failure
Application error

Logs should contain enough context to diagnose failures.

43. Ingestion Metadata

Every ingestion execution should generate metadata.

The system should track:

run_id
provider
mode
requested_from
requested_to
replay_time
started_at
completed_at
status
records_received
records_inserted
records_rejected
error_message

The mode field should distinguish:

REPLAY
LIVE

when a legitimate live provider is eventually introduced.

44. Data Freshness

The platform should track the latest known source timestamp.

Example:

Data Mode:
Historical Replay

Latest Data Timestamp:
2022-01-15

Last Ingestion Run:
2026-08-08

Source:
M5 Replay Provider

The UI must clearly distinguish replayed historical data from genuinely live data.

45. Error Handling

External providers and internal services can fail.

The architecture should handle:

Provider timeout
Provider unavailable
Invalid provider response
Rate-limit errors
Database failure
Invalid user input
Validation failure
Model inference failure
Scheduler failure

The system should return meaningful errors rather than exposing internal stack traces to users.

46. Testing Architecture

Testing should exist at multiple levels.

Unit Tests
    ↓
Integration Tests
    ↓
API Tests
    ↓
ML Pipeline Tests
    ↓
Data Leakage Tests
    ↓
End-to-End Tests

Important behaviors to test include:

Data validation
Duplicate detection
Incremental ingestion
Replay behavior
Feature generation
Temporal leakage prevention
Forecast generation
API responses
Database operations
Provider failure handling
47. V1 Deployment Architecture

The initial deployment architecture should remain simple.

Conceptually:

                    Internet
                       │
                       ▼
                React Frontend
                       │
                       ▼
                    FastAPI
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
     PostgreSQL                ML Components

The exact cloud provider and deployment strategy will be finalized later.

48. V2 MLOps Architecture

V2 will introduce model lifecycle management.

Conceptually:

Data
 ↓
Training Pipeline
 ↓
Experiment Tracking
 ↓
MLflow
 ↓
Model Evaluation
 ↓
Model Registry
 ↓
Model Deployment
 ↓
Monitoring

MLflow will provide:

Experiment tracking
Parameter tracking
Metric tracking
Model artifacts
Model versioning
Model registry
49. V2 CI/CD Architecture

The project will eventually introduce automated CI/CD.

Conceptual flow:

Developer
    ↓
Git Commit
    ↓
GitHub
    ↓
CI Pipeline
    ├── Lint
    ├── Unit Tests
    ├── Integration Tests
    ├── Build
    └── Security Checks
          ↓
      Deployment

The exact CI/CD provider and deployment target will be decided later.

50. V2 Monitoring Architecture

Monitoring will eventually cover:

Data
Data freshness
Data quality
Missing data
Data drift
Model
Prediction drift
Forecast error
Model performance degradation
Application
Latency
Errors
Request volume
Availability

Conceptually:

Data + Model + Application
            │
            ▼
        Monitoring
            │
            ▼
          Metrics
            │
            ▼
          Alerts
51. V3 Explainability Architecture

Explainability will be added after the core ML pipeline is stable.

Potential technology:

SHAP

Conceptual flow:

Input
  ↓
ML Model
  ↓
Prediction
  ↓
SHAP
  ↓
Feature Contributions

Example:

Prediction
   │
   ├── Lag Feature: Positive contribution
   ├── Rolling Mean: Positive contribution
   └── Weekend Indicator: Negative contribution

The explainability layer should describe model behavior rather than fabricate reasons.

52. V3 RAG Architecture

The RAG layer will allow the platform to use external textual evidence.

For the demand/operations domain, potential sources may include:

Business reports
Product information
Operational documentation
Promotion information
Supply-chain documents
Public business documents

Future domain adapters may use domain-specific sources.

Conceptual architecture:

Documents
    ↓
Document Ingestion
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Database

At query time:

User Question
      ↓
Retriever
      ↓
Relevant Documents
      ↓
LLM
      ↓
Evidence-backed Response

The RAG system should maintain references to retrieved evidence.

53. RAG Evaluation

RAG quality should not be judged solely by whether an answer sounds good.

Potential evaluation dimensions include:

Retrieval relevance
Retrieval recall
Citation correctness
Groundedness
Unsupported-claim rate
Answer quality

An evaluation dataset should be developed before claiming production readiness.

54. V3 LLM Architecture

The LLM should be responsible for natural-language synthesis and reasoning over available evidence.

It should not independently replace the numerical forecasting system.

Conceptually:

Forecast Model
       │
       ├──────────────┐
       │              │
       ▼              ▼
Prediction       Explainability
       │              │
       └──────┬───────┘
              ▼
          Evidence
              │
              ▼
             LLM
              │
              ▼
        User Response

The LLM should explain existing analytical outputs rather than inventing numerical predictions.

55. V4 Agentic Architecture

Agentic functionality will be introduced only after the underlying tools are stable.

The agent should interact with specialized tools.

Example:

                       User
                         │
                         ▼
                  Decision Agent
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   Forecast Tool    Analytics Tool    RAG Tool
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                      Evidence
                         │
                         ▼
                        LLM
                         │
                         ▼
                   Final Response
56. Tool Design

Each agent tool should have a clearly defined purpose.

Examples:

Forecast Tool

Returns the latest demand forecast.

Analytics Tool

Returns trend, seasonality, and anomaly information.

Explainability Tool

Returns model feature contributions.

RAG Tool

Retrieves relevant documents.

Historical Tool

Retrieves historical demand and previous predictions.

Data Quality Tool

Returns ingestion and validation information.

Monitoring Tool

Returns model and data health information.

Tools should return structured outputs rather than unstructured text wherever possible.

57. Agent Safety and Reliability

The agent should not be allowed to invent numerical results.

Numerical information should come from trusted tools.

For example:

Agent
  ↓
Forecast Tool
  ↓
Actual Model Result
  ↓
Agent Explanation

rather than:

Agent
  ↓
"Guess" Forecast

The agent should clearly distinguish:

Model output
Retrieved evidence
Generated explanation
Uncertainty
Assumptions
58. Future Domain Architecture

The long-term platform should separate domain-specific logic from reusable platform infrastructure.

Conceptually:

              Decision Intelligence Platform
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
       Demand          Finance         Supply Chain
    Intelligence     Intelligence      Intelligence
          │               │                │
          └───────────────┼────────────────┘
                          │
                    Shared Platform
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    Ingestion            MLOps              AI
        │                 │                 │
        ▼                 ▼                 ▼
     Storage          Monitoring            RAG

Future domain adapters may include:

Demand Intelligence
Financial Intelligence
Supply Chain Intelligence
Agriculture Intelligence
Manufacturing Intelligence

The shared platform should remain reusable across domains.

59. Proposed Repository Architecture

The repository will evolve incrementally.

Initial structure:

decision-intelligence-platform/
│
├── docs/
│   ├── PRD.md
│   └── SYSTEM_ARCHITECTURE.md
│
├── README.md
│
└── .gitignore

As V1 implementation begins:

decision-intelligence-platform/
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── repositories/
│   ├── schemas/
│   └── main.py
│
├── frontend/
│
├── ml/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── training/
│   └── evaluation/
│
├── data/
│   ├── ingestion/
│   ├── providers/
│   ├── validation/
│   └── processing/
│
├── database/
│
├── tests/
│
├── docs/
│
├── scripts/
│
├── README.md
│
└── .gitignore

Additional directories such as:

rag/
agents/
monitoring/
mlops/

will only be added when those capabilities are actually implemented.

60. Dependency Direction

The architecture should maintain sensible dependency direction.

Preferred:

Frontend
   ↓
API
   ↓
Services
   ↓
Domain / ML / Data Access
   ↓
Infrastructure

The frontend should not depend directly on database internals.

The ML layer should not depend on React.

The database layer should not contain business decisions.

The ingestion provider should not contain forecasting logic.

61. Configuration Management

Configuration should be separated from application code.

Potential configuration includes:

Database URL
Environment
Provider configuration
Replay clock
Model paths
Logging configuration
API credentials
Feature configuration

Development secrets should be stored through environment variables or local configuration that is excluded from Git.

Example:

.env

The .env file must not be committed if it contains secrets.

A safe example configuration file may be committed instead.

62. Environment Separation

The project should eventually support separate environments:

Development
     ↓
Testing
     ↓
Production

Each environment may have different:

Database
Provider configuration
API credentials
Logging levels
Model versions
Deployment configuration

V1 local development may begin with a simplified setup.

63. Data Lineage

The platform should eventually be able to answer:

Where did this prediction come from?

Conceptually:

Data Provider
      ↓
Raw Data
      ↓
Validated Data
      ↓
Features
      ↓
Model Version
      ↓
Prediction
      ↓
Evaluation
      ↓
Explanation
      ↓
Evidence

This becomes an important capability for MLOps and responsible AI.

64. Scalability Strategy

V1 will prioritize simplicity over horizontal scalability.

The architecture should nevertheless avoid design decisions that prevent future scaling.

If future workload increases, components may be separated or scaled independently.

For example:

Current:

FastAPI
   │
   ├── Data
   └── ML

Future:

API Service
     │
     ├── Data Service
     ├── ML Service
     ├── RAG Service
     └── Monitoring Service

This evolution should occur only when justified by actual requirements.

65. Technology Stack — Initial
Layer	Technology
Programming	Python
Data Processing	Pandas, NumPy
Machine Learning	Scikit-learn, XGBoost
Backend	FastAPI
Database	PostgreSQL
Frontend	React + TypeScript
Testing	Pytest
Version Control	Git + GitHub

Future technologies:

Capability	Planned Technology / Category
Experiment Tracking	MLflow
Model Registry	MLflow
Containerization	Docker
CI/CD	GitHub Actions
Explainability	SHAP
RAG	Embeddings + Vector Database
LLM	LLM API / Appropriate Model
Agentic AI	Tool Calling + Orchestration
Monitoring	Appropriate Observability Tools
Cloud	To be selected based on deployment requirements

Technology selections are provisional until documented in Technology Decision Records.

66. Architecture Evolution

The platform will evolve through major stages.

V1
Data + Ingestion + ML + API + UI
        │
        ▼
V2
MLOps + Deployment + Monitoring
        │
        ▼
V3
Explainability + RAG + LLM
        │
        ▼
V4
Tools + Agentic Decision Intelligence
        │
        ▼
V5
Advanced Monitoring + Cloud + AI Operations
        │
        ▼
V6
Multi-Domain Decision Intelligence

Each stage should build on the previous stage rather than creating an independent application.

67. V1 Architecture Summary

The first implementation will focus on:

M5 Historical Retail Data
            ↓
      Replay Provider
            ↓
     Automatic Ingestion
            ↓
      Data Validation
            ↓
         PostgreSQL
            ↓
    Feature Engineering
            ↓
    Demand Forecasting
            ↓
 Time-Aware Evaluation
            ↓
 Uncertainty + Anomaly
            ↓
      Decision Engine
            ↓
          FastAPI
            ↓
     React Dashboard

This is the minimum architecture required to establish the core platform.

68. V1 Architectural Boundaries

The following boundaries must remain clear:

Ingestion Layer

Responsible for obtaining data from providers.

Validation Layer

Responsible for determining whether incoming data is acceptable.

Data Layer

Responsible for storing trusted and operational data.

ML Layer

Responsible for feature engineering, training, evaluation, and inference.

Decision Layer

Responsible for transforming analytical outputs into structured decision-support information.

API Layer

Responsible for exposing platform functionality.

Presentation Layer

Responsible for user interaction and visualization.

69. Architectural Risks

Potential risks include:

Data Availability

Public demand datasets may not provide live external APIs.

Mitigation:

Use a replay provider and maintain an interchangeable provider interface.

Data Leakage

Future observations may accidentally enter training features.

Mitigation:

Strict time-aware feature construction and leakage tests.

Model Overfitting

Complex models may outperform baselines only on historical data.

Mitigation:

Time-aware validation and baseline comparison.

Scope Explosion

Introducing too many technologies too early could result in incomplete integrations.

Mitigation:

Version-based development and strict scope control.

GenAI Hallucination

LLMs may produce unsupported explanations.

Mitigation:

RAG, structured outputs, tool-based numerical retrieval, and evaluation.

70. Risk Mitigation
Risk	Mitigation
Provider failure	Retry logic, logging, provider abstraction
Rate limits	Controlled requests and caching
Schema changes	Validation layer
Data leakage	Time-aware pipelines
Poor model performance	Baseline comparison
Scope explosion	Version-based development
LLM hallucination	RAG + structured tools + evaluation
Secret leakage	Environment variables
Reproducibility problems	Versioned data/model metadata
Excessive complexity	Introduce infrastructure only when justified
71. Architectural Decisions Still Pending

The following decisions will be finalized through Technology Decision Records:

Exact initial dataset and selected subset
Replay-provider implementation strategy
Future legitimate external API provider
Raw-data storage mechanism
ORM / database access strategy
Exact forecasting target
Forecast horizon
Forecasting model selection
Feature engineering strategy
Forecast uncertainty methodology
Anomaly detection methodology
Frontend charting library
Deployment platform
Authentication mechanism
MLflow deployment strategy
Vector database
LLM provider
Agent orchestration framework
Monitoring stack
Cloud platform

These decisions should not be made merely because a technology is popular.

Each decision should be tied to a project requirement.

72. Architecture Decision Principle

Every major architectural decision should answer:

What problem does this solve?
        ↓
Why is this technology appropriate?
        ↓
What alternatives were considered?
        ↓
What trade-offs are accepted?
        ↓
How will it affect future versions?

This ensures that the project demonstrates engineering reasoning rather than technology accumulation.

73. Next Design Documents

After this architecture document, the next documents will be:

01. PRD.md
        ↓
02. SYSTEM_ARCHITECTURE.md
        ↓
03. TECHNOLOGY_DECISION_RECORDS.md
        ↓
04. DATABASE_DESIGN.md
        ↓
05. API_SPECIFICATION.md
        ↓
06. VERSION_ROADMAP.md
        ↓
07. INTERVIEW_NARRATIVE.md

Only after the core design is sufficiently stable will implementation begin.

74. Current Status

System Architecture Version: 0.2
Status: Draft

Completed:

High-level architecture
Layered architecture
Provider abstraction
Replay-provider architecture
Incremental ingestion architecture
Data validation architecture
Data quality architecture
Storage architecture
Time-series data architecture
Feature-engineering architecture
Temporal leakage prevention
Forecasting architecture
Baseline architecture
Model evaluation architecture
Prediction persistence
Anomaly detection architecture
Decision-engine architecture
Backend architecture
Frontend architecture
Testing architecture
Deployment direction
MLOps evolution
Explainability architecture
RAG architecture
Agentic architecture
Future-domain architecture
Repository evolution
Dependency direction
Configuration strategy
Data lineage
Scalability strategy
Architectural risks

Next document:

Technology Decision Records (TDRs)

The TDR document will explain why each major technology is selected, what alternatives were considered, and what trade-offs were accepted.