````markdown
# Decision Intelligence Platform

## API Specification

**Document Status:** Draft  
**Document Version:** 0.1  
**Product:** Decision Intelligence Platform  
**Initial Domain:** Retail Demand Forecasting & Operational Intelligence  
**Initial Release:** V1  
**Backend:** FastAPI  
**Database:** PostgreSQL  
**Frontend:** React + TypeScript  
**Related Documents:**
- PRD.md
- SYSTEM_ARCHITECTURE.md
- TECHNOLOGY_DECISION_RECORDS.md
- DATABASE_DESIGN.md

---

# 1. Purpose

This document defines the API contract for the Decision Intelligence Platform.

The API provides a controlled interface between:

- Frontend applications
- Data ingestion services
- Forecasting services
- Decision-support services
- PostgreSQL
- Future MLOps components
- Future RAG and LLM components
- Future agentic tools

The API should hide internal implementation details from clients.

The frontend must communicate with the backend through the API rather than directly accessing:

- PostgreSQL
- ML model files
- Data-processing code
- External data-provider credentials
- Internal service implementations

---

# 2. API Design Goals

The API should provide:

1. Clear resource boundaries.
2. Consistent request and response structures.
3. Strong input validation.
4. Predictable error handling.
5. API versioning.
6. Time-series-aware querying.
7. Pagination where appropriate.
8. Filtering and sorting where appropriate.
9. Separation between application APIs and internal services.
10. Future compatibility with MLOps, RAG, and agentic workflows.
11. A contract that can be tested independently from the frontend.
12. OpenAPI documentation through FastAPI.

---

# 3. API Technology

The V1 API will use:

```text
FastAPI
    ↓
Pydantic
    ↓
Service Layer
    ↓
Repository / Domain Layer
    ↓
PostgreSQL
````

FastAPI will automatically expose OpenAPI documentation.

Expected development URLs:

```text
Swagger UI:
http://localhost:8000/docs

ReDoc:
http://localhost:8000/redoc

OpenAPI JSON:
http://localhost:8000/openapi.json
```

These URLs are for local development and may change during deployment.

---

# 4. Base URL

All versioned application endpoints will use:

```text
/api/v1
```

Example:

```text
http://localhost:8000/api/v1/products
```

System-level health endpoints may remain outside the versioned API:

```text
/health
```

---

# 5. API Versioning

The initial API version is:

```text
v1
```

Therefore:

```text
/api/v1/...
```

Future breaking changes should introduce a new API version.

Example:

```text
/api/v1/forecasts
/api/v2/forecasts
```

The V1 API should not be changed in a breaking manner without either:

* backward-compatible migration, or
* introduction of a new API version.

---

# 6. API Resource Categories

The V1 API is divided into the following resource groups:

```text
System
│
├── Health
│
Data
│
├── Products
├── Stores
├── Demand
├── Data Freshness
│
Ingestion
│
├── Ingestion Status
├── Ingestion Runs
│
Forecasting
│
├── Forecasts
├── Predictions
│
Models
│
├── Models
├── Model Performance
│
Analytics
│
├── Anomalies
│
Future
│
├── Explainability
├── RAG
├── AI Assistant
└── Agent Tools
```

V1 will implement only the required resources.

Future resources will be added incrementally.

---

# 7. Common HTTP Methods

The API will use standard HTTP methods.

| Method | Purpose                                   |
| ------ | ----------------------------------------- |
| GET    | Retrieve data                             |
| POST   | Trigger an operation or create a resource |
| PUT    | Replace a resource                        |
| PATCH  | Partially update a resource               |
| DELETE | Remove a resource                         |

V1 will primarily use:

```text
GET
POST
```

Update and deletion endpoints will only be introduced when required.

---

# 8. Common HTTP Status Codes

| Status Code | Meaning                                      |
| ----------- | -------------------------------------------- |
| 200         | Successful request                           |
| 201         | Resource created                             |
| 202         | Request accepted for asynchronous processing |
| 204         | Successful request with no response body     |
| 400         | Invalid request                              |
| 401         | Authentication required                      |
| 403         | Access denied                                |
| 404         | Resource not found                           |
| 409         | Resource conflict                            |
| 422         | Validation error                             |
| 429         | Rate limit exceeded                          |
| 500         | Internal server error                        |
| 502         | External provider failure                    |
| 503         | Service unavailable                          |

V1 may not require authentication or rate limiting initially, but the API design should allow them to be introduced later.

---

# 9. Common Response Structure

Successful responses should return structured JSON.

Example:

```json
{
  "data": {},
  "meta": {}
}
```

For collection responses:

```json
{
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 1200
  }
}
```

The exact response structure may be simplified for endpoints where pagination is not applicable.

---

# 10. Common Error Response

All API errors should use a consistent structure.

Example:

```json
{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "The requested product was not found.",
    "details": null,
    "request_id": "8f4a5e7c"
  }
}
```

For validation errors:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more request fields are invalid.",
    "details": [
      {
        "field": "product_id",
        "message": "Product ID is required."
      }
    ],
    "request_id": "8f4a5e7c"
  }
}
```

---

# 11. Request ID

Each API request should eventually receive a unique request identifier.

Example:

```text
X-Request-ID: 8f4a5e7c
```

The request ID should be included in:

* API logs
* Error responses
* Debugging information
* Monitoring systems

This may initially be generated by the backend.

---

# 12. Health API

## 12.1 Get Application Health

```http
GET /health
```

Purpose:

Determine whether the API service is running.

Example response:

```json
{
  "status": "healthy",
  "service": "decision-intelligence-api",
  "version": "0.1.0"
}
```

HTTP status:

```text
200 OK
```

---

# 13. Readiness API

## 13.1 Get Service Readiness

```http
GET /ready
```

Purpose:

Determine whether the application is ready to serve requests.

The readiness check may eventually verify:

* Database connectivity
* Required model availability
* Required configuration
* Required dependent services

Example:

```json
{
  "status": "ready",
  "database": "ready",
  "model_service": "ready"
}
```

---

# 14. Products API

Products represent demand-forecasting entities.

---

## 14.1 List Products

```http
GET /api/v1/products
```

Purpose:

Return products available in the platform.

Query parameters:

```text
page
page_size
category
department
search
sort_by
sort_order
```

Example:

```http
GET /api/v1/products?page=1&page_size=50
```

Example response:

```json
{
  "data": [
    {
      "product_id": "A123",
      "category": "Food",
      "department": "Grocery"
    },
    {
      "product_id": "A124",
      "category": "Food",
      "department": "Grocery"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 2
  }
}
```

---

## 14.2 Get Product

```http
GET /api/v1/products/{product_id}
```

Example:

```http
GET /api/v1/products/A123
```

Example response:

```json
{
  "data": {
    "product_id": "A123",
    "category": "Food",
    "department": "Grocery"
  }
}
```

Possible errors:

```text
404 PRODUCT_NOT_FOUND
```

---

# 15. Stores API

Stores represent locations where product demand is observed.

---

## 15.1 List Stores

```http
GET /api/v1/stores
```

Query parameters:

```text
page
page_size
search
sort_by
sort_order
```

Example:

```http
GET /api/v1/stores?page=1&page_size=50
```

Example response:

```json
{
  "data": [
    {
      "store_id": "STORE_01"
    },
    {
      "store_id": "STORE_02"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 2
  }
}
```

---

## 15.2 Get Store

```http
GET /api/v1/stores/{store_id}
```

Example:

```http
GET /api/v1/stores/STORE_01
```

Example response:

```json
{
  "data": {
    "store_id": "STORE_01"
  }
}
```

Possible errors:

```text
404 STORE_NOT_FOUND
```

---

# 16. Demand API

The Demand API exposes historical and recently ingested demand observations.

---

## 16.1 Get Demand Observations

```http
GET /api/v1/demand
```

Query parameters:

```text
product_id
store_id
start_date
end_date
page
page_size
sort_order
```

Example:

```http
GET /api/v1/demand?product_id=A123&store_id=STORE_01&start_date=2022-01-01&end_date=2022-01-31
```

Example response:

```json
{
  "data": [
    {
      "product_id": "A123",
      "store_id": "STORE_01",
      "date": "2022-01-01",
      "demand": 42
    },
    {
      "product_id": "A123",
      "store_id": "STORE_01",
      "date": "2022-01-02",
      "demand": 47
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 2
  }
}
```

---

## 16.2 Get Latest Demand

```http
GET /api/v1/demand/latest
```

Query parameters:

```text
product_id
store_id
```

Example:

```http
GET /api/v1/demand/latest?product_id=A123&store_id=STORE_01
```

Example response:

```json
{
  "data": {
    "product_id": "A123",
    "store_id": "STORE_01",
    "date": "2022-01-15",
    "demand": 51
  }
}
```

---

# 17. Data Freshness API

The platform must clearly communicate how recent the available data is.

This is particularly important because V1 uses historical replay.

---

## 17.1 Get Data Freshness

```http
GET /api/v1/data-freshness
```

Query parameters:

```text
product_id
store_id
```

Example response:

```json
{
  "data": {
    "mode": "REPLAY",
    "provider": "M5ReplayProvider",
    "latest_data_timestamp": "2022-01-15",
    "last_ingestion_at": "2026-08-23T14:30:00Z",
    "status": "available"
  }
}
```

The API must never represent replayed historical data as genuinely live data.

---

# 18. Ingestion API

The ingestion API provides visibility into the data-ingestion pipeline.

---

## 18.1 Get Ingestion Status

```http
GET /api/v1/ingestion/status
```

Example response:

```json
{
  "data": {
    "provider": "M5ReplayProvider",
    "mode": "REPLAY",
    "status": "healthy",
    "latest_available_timestamp": "2022-01-15",
    "latest_ingested_timestamp": "2022-01-15",
    "last_run_id": "ing_20220823_001"
  }
}
```

---

## 18.2 Trigger Ingestion

```http
POST /api/v1/ingestion/run
```

Purpose:

Trigger an ingestion operation.

Request body:

```json
{
  "mode": "REPLAY"
}
```

Example response:

```json
{
  "data": {
    "run_id": "ing_20220823_001",
    "status": "started",
    "mode": "REPLAY"
  }
}
```

HTTP status:

```text
202 Accepted
```

The actual implementation may execute synchronously in early V1 and become asynchronous later.

---

## 18.3 Get Ingestion Run

```http
GET /api/v1/ingestion/runs/{run_id}
```

Example:

```http
GET /api/v1/ingestion/runs/ing_20220823_001
```

Example response:

```json
{
  "data": {
    "run_id": "ing_20220823_001",
    "provider": "M5ReplayProvider",
    "mode": "REPLAY",
    "requested_from": "2022-01-14",
    "requested_to": "2022-01-15",
    "replay_time": "2022-01-15",
    "started_at": "2026-08-23T14:30:00Z",
    "completed_at": "2026-08-23T14:30:05Z",
    "status": "SUCCESS",
    "records_received": 100,
    "records_inserted": 95,
    "records_rejected": 5,
    "error_message": null
  }
}
```

---

## 18.4 List Ingestion Runs

```http
GET /api/v1/ingestion/runs
```

Query parameters:

```text
page
page_size
status
mode
provider
start_date
end_date
```

Example:

```http
GET /api/v1/ingestion/runs?status=SUCCESS&page=1&page_size=20
```

---

# 19. Replay Control API

Replay controls are primarily intended for development and demonstration.

They should not necessarily be exposed in a public production API.

---

## 19.1 Get Replay Status

```http
GET /api/v1/replay/status
```

Example response:

```json
{
  "data": {
    "mode": "REPLAY",
    "replay_clock": "2022-01-15",
    "latest_dataset_timestamp": "2022-03-31",
    "latest_available_timestamp": "2022-01-15"
  }
}
```

---

## 19.2 Advance Replay Clock

```http
POST /api/v1/replay/advance
```

Request:

```json
{
  "days": 1
}
```

Example response:

```json
{
  "data": {
    "previous_timestamp": "2022-01-15",
    "new_timestamp": "2022-01-16"
  }
}
```

---

## 19.3 Reset Replay

```http
POST /api/v1/replay/reset
```

Request:

```json
{
  "timestamp": "2022-01-01"
}
```

Example response:

```json
{
  "data": {
    "replay_clock": "2022-01-01",
    "status": "reset"
  }
}
```

---

# 20. Forecast API

Forecasts represent future demand predictions generated by a registered model.

---

## 20.1 Get Forecast

```http
GET /api/v1/forecasts
```

Query parameters:

```text
product_id
store_id
forecast_date
start_date
end_date
model_id
model_version
```

Example:

```http
GET /api/v1/forecasts?product_id=A123&store_id=STORE_01
```

Example response:

```json
{
  "data": [
    {
      "product_id": "A123",
      "store_id": "STORE_01",
      "target_date": "2022-01-16",
      "predicted_demand": 124,
      "lower_bound": 110,
      "upper_bound": 139,
      "model_id": "xgboost_demand",
      "model_version": "1.0.0",
      "prediction_timestamp": "2022-01-15T23:00:00Z"
    }
  ]
}
```

---

# 21. Forecast by Product and Store

## 21.1 Get Specific Forecast

```http
GET /api/v1/forecasts/{product_id}/{store_id}
```

Example:

```http
GET /api/v1/forecasts/A123/STORE_01
```

Query parameters:

```text
horizon
```

Example:

```http
GET /api/v1/forecasts/A123/STORE_01?horizon=7
```

Example response:

```json
{
  "data": {
    "product_id": "A123",
    "store_id": "STORE_01",
    "forecast_horizon": 7,
    "model_id": "xgboost_demand",
    "model_version": "1.0.0",
    "forecasts": [
      {
        "target_date": "2022-01-16",
        "predicted_demand": 124,
        "lower_bound": 110,
        "upper_bound": 139
      },
      {
        "target_date": "2022-01-17",
        "predicted_demand": 128,
        "lower_bound": 113,
        "upper_bound": 143
      }
    ]
  }
}
```

---

# 22. Prediction API

Predictions are persisted forecast records that can later be compared against actual demand.

---

## 22.1 Get Predictions

```http
GET /api/v1/predictions
```

Query parameters:

```text
product_id
store_id
model_id
model_version
start_date
end_date
page
page_size
```

Example:

```http
GET /api/v1/predictions?product_id=A123&store_id=STORE_01&page=1&page_size=50
```

Example response:

```json
{
  "data": [
    {
      "prediction_id": "pred_001",
      "product_id": "A123",
      "store_id": "STORE_01",
      "prediction_timestamp": "2022-01-15T23:00:00Z",
      "target_date": "2022-01-16",
      "predicted_value": 124,
      "actual_value": null,
      "error": null,
      "model_id": "xgboost_demand",
      "model_version": "1.0.0"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 1
  }
}
```

---

# 23. Model API

The Model API exposes metadata about forecasting models.

---

## 23.1 List Models

```http
GET /api/v1/models
```

Query parameters:

```text
status
model_type
page
page_size
```

Example response:

```json
{
  "data": [
    {
      "model_id": "xgboost_demand",
      "model_type": "XGBoost",
      "version": "1.0.0",
      "status": "ACTIVE",
      "created_at": "2026-08-23T10:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 1
  }
}
```

---

## 23.2 Get Model

```http
GET /api/v1/models/{model_id}
```

Example:

```http
GET /api/v1/models/xgboost_demand
```

Example response:

```json
{
  "data": {
    "model_id": "xgboost_demand",
    "model_type": "XGBoost",
    "version": "1.0.0",
    "status": "ACTIVE",
    "training_data_start": "2022-01-01",
    "training_data_end": "2022-02-28",
    "feature_version": "1.0.0",
    "created_at": "2026-08-23T10:00:00Z"
  }
}
```

---

# 24. Model Performance API

The API exposes historical evaluation results.

---

## 24.1 Get Model Performance

```http
GET /api/v1/models/{model_id}/performance
```

Query parameters:

```text
model_version
start_date
end_date
product_id
store_id
```

Example response:

```json
{
  "data": {
    "model_id": "xgboost_demand",
    "model_version": "1.0.0",
    "metrics": {
      "mae": 8.21,
      "rmse": 11.43,
      "mape": 12.8,
      "bias": -0.7
    },
    "baseline_comparison": {
      "baseline_model": "seasonal_naive",
      "baseline_mae": 10.54,
      "model_mae": 8.21
    }
  }
}
```

---

# 25. Anomaly API

The anomaly API exposes unusual demand patterns.

---

## 25.1 Get Anomalies

```http
GET /api/v1/anomalies
```

Query parameters:

```text
product_id
store_id
start_date
end_date
severity
page
page_size
```

Example response:

```json
{
  "data": [
    {
      "anomaly_id": "anom_001",
      "product_id": "A123",
      "store_id": "STORE_01",
      "date": "2022-01-15",
      "observed_demand": 12,
      "expected_demand": 45,
      "severity": "HIGH",
      "score": 0.92
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 1
  }
}
```

---

# 26. Decision Intelligence API

The Decision API provides a combined view of the information required for decision support.

Instead of requiring the frontend to call many endpoints separately, this endpoint can eventually provide a consolidated response.

---

## 26.1 Get Decision Summary

```http
GET /api/v1/decision-summary
```

Query parameters:

```text
product_id
store_id
horizon
```

Example:

```http
GET /api/v1/decision-summary?product_id=A123&store_id=STORE_01&horizon=7
```

Example response:

```json
{
  "data": {
    "product_id": "A123",
    "store_id": "STORE_01",
    "forecast": {
      "horizon": 7,
      "expected_demand": 124,
      "lower_bound": 110,
      "upper_bound": 139
    },
    "trend": {
      "direction": "INCREASING",
      "strength": 0.72
    },
    "anomaly": {
      "detected": true,
      "severity": "MEDIUM"
    },
    "model": {
      "model_id": "xgboost_demand",
      "version": "1.0.0",
      "mae": 8.21
    },
    "data": {
      "mode": "REPLAY",
      "latest_timestamp": "2022-01-15"
    }
  }
}
```

This endpoint represents the core V1 idea of **Decision Intelligence**.

---

# 27. Data Quality API

The platform should eventually expose data-quality information.

---

## 27.1 Get Data Quality Summary

```http
GET /api/v1/data-quality
```

Query parameters:

```text
start_date
end_date
provider
```

Example response:

```json
{
  "data": {
    "records_received": 10000,
    "records_valid": 9850,
    "records_rejected": 150,
    "duplicate_records": 20,
    "missing_values": 75,
    "validation_error_rate": 0.015,
    "status": "HEALTHY"
  }
}
```

---

# 28. Future Explainability API

Explainability will be introduced after the core forecasting system is stable.

---

## 28.1 Get Prediction Explanation

```http
GET /api/v1/explanations/{prediction_id}
```

Future response:

```json
{
  "data": {
    "prediction_id": "pred_001",
    "method": "SHAP",
    "prediction": 124,
    "features": [
      {
        "feature": "lag_7",
        "value": 118,
        "contribution": 7.2
      },
      {
        "feature": "rolling_mean_7",
        "value": 115,
        "contribution": 5.1
      }
    ]
  }
}
```

This endpoint is not required for the initial V1 implementation.

---

# 29. Future RAG API

RAG will be introduced in a later version.

Potential resources:

```text
/api/v1/documents
/api/v1/documents/{document_id}
/api/v1/search
```

---

## 29.1 Search Documents

Future endpoint:

```http
POST /api/v1/search
```

Request:

```json
{
  "query": "Why did demand increase during this period?",
  "top_k": 5
}
```

Future response:

```json
{
  "data": {
    "query": "Why did demand increase during this period?",
    "results": [
      {
        "document_id": "doc_001",
        "score": 0.91,
        "content": "Relevant document content...",
        "metadata": {
          "source": "business_report",
          "date": "2022-01-10"
        }
      }
    ]
  }
}
```

The actual RAG API will be specified in a future version.

---

# 30. Future AI Assistant API

The LLM assistant will be introduced after the underlying analytical tools are stable.

Potential endpoint:

```http
POST /api/v1/assistant/query
```

Request:

```json
{
  "question": "Why is demand expected to increase next week?",
  "product_id": "A123",
  "store_id": "STORE_01"
}
```

Future response:

```json
{
  "data": {
    "answer": "Demand is expected to increase based on recent demand trends and historical patterns.",
    "evidence": [],
    "tools_used": [
      "forecast_tool",
      "analytics_tool",
      "rag_tool"
    ]
  }
}
```

The assistant should not independently invent numerical forecasts.

Numerical values should come from trusted platform tools.

---

# 31. Future Agent Tool APIs

Agentic functionality will eventually use structured tools.

Potential tools:

```text
Forecast Tool
Analytics Tool
Historical Demand Tool
Anomaly Tool
Explainability Tool
RAG Search Tool
Data Quality Tool
Monitoring Tool
```

Conceptually:

```text
User
  ↓
Agent
  ↓
Tool Selection
  ↓
Structured Tool
  ↓
Trusted Platform Result
  ↓
Agent
  ↓
Final Response
```

The exact tool schemas will be defined separately when V4 begins.

---

# 32. Pagination

Collection endpoints should support pagination where large datasets are expected.

Default:

```text
page = 1
page_size = 50
```

Maximum:

```text
page_size = 500
```

Example:

```http
GET /api/v1/demand?page=2&page_size=100
```

Response:

```json
{
  "data": [],
  "meta": {
    "page": 2,
    "page_size": 100,
    "total": 1250,
    "total_pages": 13
  }
}
```

---

# 33. Filtering

Filtering should be performed through query parameters.

Example:

```http
GET /api/v1/demand?product_id=A123&store_id=STORE_01
```

Multiple filters should be combined using standard query parameters.

The backend must validate filter values.

---

# 34. Date and Time Format

All API dates should use ISO 8601-compatible formats.

Date:

```text
YYYY-MM-DD
```

Example:

```text
2022-01-15
```

Datetime:

```text
YYYY-MM-DDTHH:MM:SSZ
```

Example:

```text
2026-08-23T14:30:00Z
```

The API should use UTC for system timestamps.

Domain dates such as demand dates should retain their intended business meaning.

---

# 35. Forecast Horizon

Forecast requests may specify a horizon.

Example:

```http
GET /api/v1/forecasts/A123/STORE_01?horizon=7
```

The backend should validate:

```text
horizon >= 1
```

The maximum horizon should be configured according to the model's supported forecast range.

The API must not request a horizon that the active model cannot support.

---

# 36. Sorting

Where sorting is supported:

```text
sort_by
sort_order
```

Example:

```http
GET /api/v1/products?sort_by=product_id&sort_order=asc
```

Allowed values should be explicitly validated.

The API should reject unsupported sorting fields rather than constructing unsafe database queries.

---

# 37. Authentication Strategy

Authentication is not required for the first local V1 implementation.

The API architecture should nevertheless allow authentication to be added later.

Potential future architecture:

```text
Client
  ↓
Authentication
  ↓
Authorization
  ↓
FastAPI
```

Potential mechanisms may include:

* JWT
* OAuth2
* Cloud identity provider

The final authentication technology will be decided through a future Technology Decision Record.

---

# 38. Authorization Strategy

Future authorization may distinguish:

```text
Admin
Analyst
Viewer
Service
Agent
```

Example:

```text
Admin
 ├── Trigger ingestion
 ├── Manage models
 └── Manage system configuration

Analyst
 ├── View forecasts
 ├── View analytics
 └── Query decision summaries

Viewer
 └── Read-only access
```

This is future functionality.

---

# 39. Rate Limiting

Rate limiting is not required for the initial local implementation.

Future production deployments should consider rate limits for:

* Public APIs
* AI assistant endpoints
* RAG search
* Agent endpoints
* Expensive model operations

Potential response:

```text
429 Too Many Requests
```

---

# 40. API Security

The API must never expose:

* Database credentials
* External provider API keys
* LLM API keys
* Internal filesystem paths
* Model secrets
* Environment secrets

Secrets must be managed through environment variables or an appropriate secret-management system.

---

# 41. External Provider Security

The provider layer is responsible for external-provider credentials.

Conceptually:

```text
FastAPI
   │
   X
   │
External API Credentials

Ingestion Service
   │
   ▼
Provider Adapter
   │
   ▼
External Provider
```

The frontend must never receive provider credentials.

---

# 42. API Idempotency

Operations that may be retried should be designed to avoid duplicate effects.

This is particularly important for ingestion.

Example:

```text
Provider
   ↓
Record A
   ↓
Ingestion
   ↓
Already exists
   ↓
Do not create duplicate
```

The database should enforce appropriate uniqueness constraints.

---

# 43. Ingestion Idempotency

A demand observation should be uniquely identified using the appropriate business key.

Conceptually:

```text
product_id
+
store_id
+
date
```

This allows the ingestion service to detect duplicate observations.

The exact database constraint is defined in:

```text
DATABASE_DESIGN.md
```

---

# 44. API and Database Separation

The API must not expose database tables directly.

Bad design:

```text
GET /api/v1/table/demand_observations
```

Preferred design:

```text
GET /api/v1/demand
```

The API represents domain resources rather than raw database implementation details.

---

# 45. API and ML Separation

The API should not directly expose internal model implementation.

Bad:

```text
POST /api/v1/xgboost/predict
```

Preferred:

```text
GET /api/v1/forecasts/{product_id}/{store_id}
```

This allows the underlying model to change without changing the user-facing API.

For example:

```text
XGBoost
   ↓
LightGBM
   ↓
Transformer
```

can change while the forecast endpoint remains stable.

---

# 46. API and Decision Engine Separation

The Decision Engine should aggregate information from multiple services.

Conceptually:

```text
Forecast Service
      │
Analytics Service
      │
Anomaly Service
      │
Model Service
      │
Data Quality Service
      │
      ▼
Decision Engine
      │
      ▼
FastAPI
```

This prevents the frontend from needing to understand internal service dependencies.

---

# 47. Frontend API Usage

The React frontend will communicate only with FastAPI.

Example:

```text
React
   │
   ├── GET /api/v1/products
   ├── GET /api/v1/stores
   ├── GET /api/v1/demand
   ├── GET /api/v1/forecasts
   ├── GET /api/v1/anomalies
   ├── GET /api/v1/data-freshness
   └── GET /api/v1/decision-summary
```

The frontend should not contain forecasting logic.

---

# 48. API Client Layer

The React application should use a dedicated API client layer.

Conceptually:

```text
frontend/
│
├── api/
│   ├── client.ts
│   ├── products.ts
│   ├── stores.ts
│   ├── demand.ts
│   ├── forecasts.ts
│   ├── models.ts
│   └── ingestion.ts
```

This keeps API communication separate from UI components.

---

# 49. API Testing

Every endpoint should eventually have automated tests.

Testing levels:

```text
Schema Tests
     ↓
Unit Tests
     ↓
API Tests
     ↓
Integration Tests
     ↓
End-to-End Tests
```

Examples:

```text
GET /health
GET /products
GET /demand
GET /forecasts
GET /models
GET /anomalies
GET /decision-summary
```

---

# 50. Important API Test Cases

The test suite should cover:

### Valid Requests

```text
Valid product ID
Valid store ID
Valid date range
Valid forecast horizon
```

### Invalid Requests

```text
Unknown product
Unknown store
Invalid date
Invalid date range
Negative horizon
Unsupported sorting field
Invalid pagination
```

### System Failures

```text
Database unavailable
Model unavailable
Provider unavailable
Timeout
Unexpected provider response
```

---

# 51. API Observability

Future production monitoring should track:

* Request count
* Response time
* Error rate
* Endpoint latency
* Status codes
* Database latency
* Model inference latency
* External provider latency

Example:

```text
API Request
    ↓
Request ID
    ↓
Logs
    ↓
Metrics
    ↓
Monitoring
```

---

# 52. API Performance

V1 will prioritize correctness and maintainability over premature optimization.

Potential future optimizations include:

* Database indexes
* Response caching
* Redis
* Asynchronous processing
* Batch prediction
* Query optimization
* Background workers

These should only be introduced when actual performance requirements justify them.

---

# 53. Asynchronous Operations

Some operations may eventually be too expensive for synchronous HTTP requests.

Examples:

```text
Model training
Large ingestion
Batch forecasting
Document ingestion
Embedding generation
RAG indexing
Agent workflows
```

Future architecture:

```text
POST /operation
      ↓
202 Accepted
      ↓
Background Job
      ↓
Job ID
      ↓
GET /jobs/{job_id}
```

V1 may initially use synchronous execution for simple operations.

---

# 54. Future Job API

Potential future endpoints:

```text
POST /api/v1/jobs
GET /api/v1/jobs/{job_id}
POST /api/v1/jobs/{job_id}/cancel
```

These will be introduced only when asynchronous processing becomes necessary.

---

# 55. API Contract for V1

The minimum V1 API should include:

```text
GET  /health
GET  /ready

GET  /api/v1/products
GET  /api/v1/products/{product_id}

GET  /api/v1/stores
GET  /api/v1/stores/{store_id}

GET  /api/v1/demand
GET  /api/v1/demand/latest

GET  /api/v1/data-freshness

GET  /api/v1/ingestion/status
GET  /api/v1/ingestion/runs
GET  /api/v1/ingestion/runs/{run_id}
POST /api/v1/ingestion/run

GET  /api/v1/replay/status
POST /api/v1/replay/advance
POST /api/v1/replay/reset

GET  /api/v1/forecasts
GET  /api/v1/forecasts/{product_id}/{store_id}

GET  /api/v1/predictions

GET  /api/v1/models
GET  /api/v1/models/{model_id}
GET  /api/v1/models/{model_id}/performance

GET  /api/v1/anomalies

GET  /api/v1/data-quality

GET  /api/v1/decision-summary
```

---

# 56. V1 API Architecture

The complete V1 API flow is:

```text
                         React
                           │
                           ▼
                     FastAPI API
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       Demand          Forecast          Analytics
        API              API               API
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    Decision Engine
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      PostgreSQL       ML Services       Data Services
                           │
                           ▼
                     Forecast Models
```

---

# 57. Future API Architecture

As the platform evolves:

```text
                         React
                           │
                           ▼
                     FastAPI API
                           │
                  ┌────────┴────────┐
                  │                 │
                  ▼                 ▼
           Decision Services    AI Services
                  │                 │
        ┌─────────┼─────────┐       │
        │         │         │       │
        ▼         ▼         ▼       ▼
    Forecast   Analytics  RAG     Agent
       Tool       Tool    Tool    Tools
        │         │         │       │
        └─────────┼─────────┘       │
                  │                 │
                  └────────┬────────┘
                           ▼
                         LLM
```

The future AI layer should use the same trusted analytical APIs and tools rather than bypassing them.

---

# 58. API Design Principle for Agentic AI

When V4 introduces agents, the agent should interact with structured capabilities.

For example:

```text
Agent
  ↓
forecast_tool
  ↓
GET /api/v1/forecasts/...
```

or an internal service interface equivalent to the API.

The agent should not directly access:

* PostgreSQL
* Raw model artifacts
* Provider credentials
* Internal filesystem

This maintains the same architectural boundaries established in V1.

---

# 59. API Compatibility Strategy

The following should remain stable across future versions wherever possible:

```text
Product identifiers
Store identifiers
Demand representation
Forecast resource concept
Model metadata concept
Prediction concept
Data freshness concept
```

Internal implementations may change without necessarily changing the public API.

For example:

```text
V1:
XGBoost

V2:
MLflow registered XGBoost

V3:
Different forecasting model

V4:
Multiple forecasting models
```

The forecast API can remain conceptually stable.

---

# 60. API Documentation

FastAPI should generate interactive API documentation automatically.

Development workflow:

```text
Write Pydantic Schemas
        ↓
Define FastAPI Routes
        ↓
OpenAPI Generated
        ↓
Swagger UI
        ↓
API Testing
```

The API specification in this document represents the intended contract.

The generated OpenAPI schema will become the implementation-level source of truth once the API is implemented.

---

# 61. API Implementation Principles

The implementation should follow:

```text
Router
  ↓
Schema Validation
  ↓
Service
  ↓
Domain Logic
  ↓
Repository / ML Component
  ↓
Database / Model
```

Avoid putting:

* SQL queries
* ML logic
* feature engineering
* provider communication

directly inside FastAPI route functions.

---

# 62. Recommended Backend Structure

The API implementation should eventually follow a structure similar to:

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       │   ├── health.py
│   │       │   ├── products.py
│   │       │   ├── stores.py
│   │       │   ├── demand.py
│   │       │   ├── ingestion.py
│   │       │   ├── forecasts.py
│   │       │   ├── predictions.py
│   │       │   ├── models.py
│   │       │   ├── anomalies.py
│   │       │   └── decisions.py
│   │       │
│   │       └── router.py
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │
│   ├── repositories/
│   │
│   ├── core/
│   │
│   └── models/
│
└── tests/
```

The exact implementation may evolve.

---

# 63. V1 API Scope Control

The following should NOT be implemented merely because they appear in future architecture documents:

```text
Authentication
Redis
Graph Database
MCP
Multi-agent orchestration
LLM assistant
RAG
Vector database
STT
TTS
Multimodal processing
Kubernetes
Kafka
Complex microservices
```

These belong to later versions unless a genuine V1 requirement emerges.

The goal is to keep V1 complete rather than overloaded.

---

# 64. Definition of API Completion for V1

The V1 API will be considered complete when:

* Health endpoints work.
* Product endpoints work.
* Store endpoints work.
* Demand endpoints work.
* Data freshness is exposed.
* Ingestion status is exposed.
* Ingestion runs are recorded.
* Replay controls work.
* Forecasts can be retrieved.
* Predictions can be retrieved.
* Model metadata can be retrieved.
* Model performance can be retrieved.
* Anomalies can be retrieved.
* Data quality can be retrieved.
* Decision summaries can be retrieved.
* Validation errors are handled consistently.
* API errors use a consistent structure.
* API documentation is generated through FastAPI.
* Automated API tests exist.
* The React frontend can consume the required endpoints.

---

# 65. V1 API Success Criteria

The API should enable the following complete user flow:

```text
User
 ↓
React Dashboard
 ↓
Select Product
 ↓
Select Store
 ↓
Request Decision Summary
 ↓
FastAPI
 ↓
Decision Engine
 ↓
Forecast + Historical Data
 + Model Performance
 + Anomaly Information
 + Data Freshness
 ↓
Structured Response
 ↓
React Dashboard
 ↓
Human Decision Support
```

The user should be able to understand:

```text
What is expected?
How uncertain is it?
How has demand behaved historically?
Is anything unusual?
Which model produced the result?
How well has that model performed?
How fresh is the underlying data?
```

---

# 66. Future Evolution

The API will evolve in stages.

```text
V1
│
├── Data APIs
├── Ingestion APIs
├── Forecast APIs
├── Model APIs
├── Analytics APIs
└── Decision Summary API
        │
        ▼
V2
│
├── MLOps APIs
├── Model Registry APIs
├── Monitoring APIs
└── Deployment Operations
        │
        ▼
V3
│
├── Explainability APIs
├── Document APIs
├── Retrieval APIs
└── Assistant APIs
        │
        ▼
V4
│
├── Tool APIs
├── Agent APIs
├── Workflow APIs
└── Evaluation APIs
```

Each version should extend the existing platform rather than creating a separate application.

---

# 67. Final V1 API Contract

The V1 API is therefore centered around:

```text
                         Decision Intelligence API
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │                           │                           │
       ▼                           ▼                           ▼
     DATA                      FORECASTING                 ANALYTICS
       │                           │                           │
       ├── Products                ├── Forecasts               ├── Anomalies
       ├── Stores                  ├── Predictions              ├── Model Performance
       ├── Demand                  └── Models                   └── Data Quality
       └── Freshness
       │
       ▼
   INGESTION
       │
       ├── Status
       ├── Runs
       └── Replay Control
       │
       └──────────────────────────────┐
                                      ▼
                              DECISION SUMMARY
                                      │
                                      ▼
                                  React UI
```

The API therefore provides the foundation for the complete Decision Intelligence Platform.

---

# 68. Document Status

**Document Version:** 0.1
**Status:** Draft

Completed:

* API architecture
* Base URL
* API versioning
* HTTP methods
* Status codes
* Error handling
* Request IDs
* Health APIs
* Product APIs
* Store APIs
* Demand APIs
* Data freshness APIs
* Ingestion APIs
* Replay APIs
* Forecast APIs
* Prediction APIs
* Model APIs
* Model performance APIs
* Anomaly APIs
* Decision Summary API
* Data Quality API
* Future Explainability API
* Future RAG API
* Future Assistant API
* Future Agent Tool architecture
* Pagination
* Filtering
* Date/time conventions
* Forecast horizon
* Authentication strategy
* Authorization strategy
* Security
* Idempotency
* Testing
* Observability
* Performance strategy
* Asynchronous-operation strategy
* Frontend integration
* Future API evolution
* V1 completion criteria

Next design/implementation step:

> **Finalize the V1 repository structure and begin implementing the data-ingestion foundation: `DemandDataProvider → M5ReplayProvider → Ingestion Service → Validation → PostgreSQL`.**

The API should be implemented incrementally alongside the underlying services rather than creating empty endpoints without working functionality.

```
```
