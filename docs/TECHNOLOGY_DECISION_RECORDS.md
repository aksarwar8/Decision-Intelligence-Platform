# Decision Intelligence Platform

## Technology Decision Records (TDR)

**Document Status:** Draft  
**Document Version:** 0.1  
**Product:** Decision Intelligence Platform  
**Initial Domain:** Indian Financial Market Intelligence  
**Related Documents:**

- `PRD.md`
- `SYSTEM_ARCHITECTURE.md`

---

# 1. Purpose

This document records the major technology and architecture decisions made for the Decision Intelligence Platform.

The purpose is not simply to document which technologies are being used.

Each decision should explain:

1. What problem needs to be solved?
2. What options were considered?
3. Why was the selected technology chosen?
4. What trade-offs were accepted?
5. What alternatives were rejected?
6. Under what circumstances should the decision be reconsidered?

This document will evolve as the project develops.

---

# 2. Technology Decision Principles

The following principles will guide technology selection.

### Principle 1 — Requirement First

A technology should be selected because it solves a project requirement.

It should not be selected merely because it is popular.

### Principle 2 — Simplicity First

Prefer the simplest technology that satisfies the requirement.

### Principle 3 — Industry Relevance

When two technologies satisfy the requirement equally well, prefer the one that provides stronger exposure to technologies commonly used in relevant industry roles.

### Principle 4 — Learning Value

Because this is also a learning project, selected technologies should provide meaningful opportunities to understand production engineering concepts.

### Principle 5 — Avoid Technology Collection

The project should not become a collection of tools.

Every technology must have a clear responsibility.

### Principle 6 — Reconsider When Requirements Change

A decision that is correct for V1 may not be correct for V4.

Technology decisions may therefore be revisited as the platform grows.

---

# 3. Decision Status

Each decision will have one of the following statuses:

| Status | Meaning |
|---|---|
| Proposed | Under consideration |
| Accepted | Selected for implementation |
| Rejected | Considered but not selected |
| Superseded | Previously selected but replaced |
| Deferred | Decision intentionally postponed |

---

# 4. TDR-001 — Programming Language

**Decision:** Use Python

**Status:** Accepted

## Context

The platform requires:

- Data processing
- Machine learning
- API development
- Automation
- MLOps
- Generative AI
- RAG
- Agentic workflows

Python provides a common language across these components.

## Options Considered

- Python
- Java
- JavaScript / TypeScript

## Decision

Python will be the primary backend, data, ML, and AI language.

## Reasoning

Python provides strong ecosystem support across:

```text
Data Science
    ↓
Machine Learning
    ↓
FastAPI
    ↓
MLOps
    ↓
LLMs
    ↓
RAG
    ↓
Agentic AI
```

It also aligns strongly with the internship roles being targeted.

## Trade-offs

Python may not provide the same raw performance as lower-level languages for every workload.

For this project, development speed, ecosystem, and ML/AI integration are more important.

## Reconsider If

A future workload introduces a performance-critical component that cannot reasonably be handled by Python.

---

# 5. TDR-002 — Data Processing

**Decision:** Use Pandas and NumPy

**Status:** Accepted

## Context

V1 requires:

- Data cleaning
- Transformation
- Feature engineering
- Exploratory analysis
- Numerical computation

## Options Considered

- Pandas + NumPy
- Polars
- PySpark

## Decision

Use:

- Pandas for tabular/time-series processing
- NumPy for numerical operations

## Reasoning

The V1 workload does not require distributed processing.

Pandas and NumPy provide a strong foundation for understanding the data-processing pipeline before introducing distributed systems.

They are also directly relevant to data-science internship requirements.

## Why Not PySpark?

PySpark is valuable for large-scale distributed processing, but introducing it in V1 would add complexity without solving an actual V1 requirement.

PySpark may be considered in a future version if the platform processes sufficiently large datasets.

## Why Not Polars?

Polars is a strong alternative, but using Pandas initially provides broader alignment with the current learning and internship objectives.

Polars may be evaluated later if performance becomes a meaningful concern.

---

# 6. TDR-003 — Machine Learning Framework

**Decision:** Use Scikit-learn

**Status:** Accepted

## Context

V1 requires:

- Baseline models
- Feature processing
- Model training
- Evaluation
- Validation
- Anomaly detection

## Options Considered

- Scikit-learn
- XGBoost
- TensorFlow
- PyTorch

## Decision

Scikit-learn will be the primary general-purpose ML framework.

XGBoost may be used for selected experiments.

## Reasoning

Scikit-learn provides:

- preprocessing
- model selection
- metrics
- validation utilities
- anomaly detection
- pipelines

It allows the project to focus on correct time-series methodology rather than framework complexity.

## Role of XGBoost

XGBoost will be considered when the feature-engineered forecasting formulation is suitable for gradient-boosted trees.

It should not automatically be assumed to be the best model.

## Why Not Deep Learning Initially?

Deep-learning models such as LSTM or Transformers may be useful for some sequence problems, but they should not be introduced simply because they are advanced.

They should be evaluated only if:

- the data supports them,
- the problem formulation benefits from them,
- and simpler baselines have been established.

---

# 7. TDR-004 — Backend Framework

**Decision:** Use FastAPI

**Status:** Accepted

## Context

The platform needs a backend API for:

- Market data
- Analytics
- Predictions
- Model information
- Future AI tools

## Options Considered

- FastAPI
- Flask
- Django

## Decision

Use FastAPI.

## Reasoning

FastAPI provides:

- Python integration
- Automatic API documentation
- Request validation
- Type-based schemas
- Async support
- Good fit for ML/AI services

It also creates a clean separation:

```text
React
  ↓
FastAPI
  ↓
ML / Services / Database
```

## Why Not Flask?

Flask is lightweight and capable, but FastAPI provides stronger built-in API schema and validation capabilities for this project.

## Why Not Django?

Django provides a much larger web framework and ORM ecosystem.

The project does not require the full Django framework for V1.

---

# 8. TDR-005 — Frontend Framework

**Decision:** Use React + TypeScript

**Status:** Accepted

## Context

The platform requires an interactive dashboard rather than a simple notebook or static page.

## Options Considered

- React + TypeScript
- Streamlit
- Vue
- Plain HTML/JavaScript

## Decision

Use React + TypeScript.

## Reasoning

The project is intended to demonstrate:

- Frontend engineering
- API integration
- Component architecture
- Interactive dashboards
- Production-oriented application development

React provides a stronger demonstration of these capabilities than a notebook-style UI.

TypeScript adds type safety to the frontend.

## Why Not Streamlit?

Streamlit is excellent for rapid ML prototypes.

However, this project is intended to demonstrate a separation between:

```text
Frontend
   ↓
API
   ↓
Backend
```

Therefore React is more appropriate for the flagship version.

Streamlit may still be useful for temporary experimentation.

---

# 9. TDR-006 — Database

**Decision:** Use PostgreSQL

**Status:** Accepted

## Context

The platform requires persistent storage for:

- Assets
- Market observations
- Predictions
- Model metadata
- Ingestion metadata

## Options Considered

- PostgreSQL
- MySQL
- SQLite
- MongoDB

## Decision

Use PostgreSQL.

## Reasoning

PostgreSQL provides:

- Relational data modeling
- Strong consistency
- SQL
- Indexing
- Constraints
- Transaction support
- Mature production ecosystem

The project also needs to demonstrate SQL skills relevant to data-science and data-engineering roles.

## Why Not SQLite?

SQLite is excellent for local prototypes but is less representative of a production-oriented multi-component application.

SQLite may still be used for isolated experiments if useful.

## Why Not MongoDB?

The core V1 data is naturally relational:

```text
Assets
    ↓
Market Observations
    ↓
Predictions
    ↓
Models
```

A relational database is therefore appropriate.

---

# 10. TDR-007 — API Data Provider Architecture

**Decision:** Use a provider abstraction

**Status:** Accepted

## Context

The platform depends on external market data.

Market-data providers may differ in:

- API format
- Authentication
- Rate limits
- Historical availability
- Licensing
- Reliability

## Decision

The application will depend on an internal `MarketDataProvider` interface rather than directly depending on one provider.

Conceptually:

```text
MarketDataProvider
       │
       ├── Indian Market Provider
       ├── Backup Provider
       └── Future Provider
```

## Reasoning

This provides:

- Provider independence
- Easier testing
- Easier replacement
- Cleaner architecture
- Reduced vendor coupling

## Important Constraint

The actual provider must be selected based on:

- Data availability
- Indian-market coverage
- API reliability
- Terms of use
- Cost
- Historical data availability

The provider decision remains separate from the architectural abstraction.

---

# 11. TDR-008 — Data Validation

**Decision:** Introduce an explicit validation layer

**Status:** Accepted

## Context

External market data cannot be assumed to be clean.

Invalid data can corrupt:

- Database records
- Features
- Model training
- Predictions

## Decision

Validation will occur before data reaches downstream ML components.

Conceptually:

```text
External API
     ↓
Raw Data
     ↓
Validation
     ↓
Processed Data
     ↓
ML
```

## Validation Examples

- Schema
- Types
- Missing values
- Duplicates
- Timestamp consistency
- Numerical constraints

## Reasoning

Data quality is a critical part of production ML systems.

---

# 12. TDR-009 — Database Access Pattern

**Decision:** Separate database access from business logic

**Status:** Proposed

## Context

The backend should not mix SQL/database operations directly with API routing and business logic.

## Proposed Architecture

```text
API Router
    ↓
Service Layer
    ↓
Repository / Data Access
    ↓
PostgreSQL
```

## Reasoning

This improves:

- Testability
- Maintainability
- Separation of concerns

The exact ORM/query strategy will be decided during database design.

---

# 13. TDR-010 — Testing Framework

**Decision:** Use Pytest

**Status:** Accepted

## Context

The project needs:

- Unit tests
- Integration tests
- API tests
- ML pipeline tests

## Decision

Use Pytest as the primary Python testing framework.

## Reasoning

Pytest provides a flexible testing model and integrates well with Python applications.

Testing will be introduced alongside implementation rather than added only after development.

---

# 14. TDR-011 — Version Control

**Decision:** Use Git + GitHub

**Status:** Accepted

## Context

The project requires:

- Version history
- Collaboration
- Branching
- Pull requests
- CI/CD integration
- Portfolio visibility

## Decision

Use Git for version control and GitHub for repository hosting.

## Reasoning

Git and GitHub provide the foundation for:

```text
Code
 ↓
Version History
 ↓
Pull Requests
 ↓
CI/CD
 ↓
Deployment
```

The repository will also contain architecture and engineering documentation.

---

# 15. TDR-012 — Containerization

**Decision:** Use Docker in V2

**Status:** Deferred

## Context

The application will eventually contain multiple components:

```text
React
FastAPI
PostgreSQL
ML
Future AI services
```

Containerization can make these components easier to reproduce and deploy.

## Decision

Docker will be introduced after the core V1 application works.

## Why Not Immediately?

Introducing Docker before the application architecture is stable can add unnecessary complexity.

The learning goal is to understand:

```text
Application
 ↓
Containerization
 ↓
Deployment
```

rather than hiding application problems behind infrastructure.

## Planned V2 Flow

```text
Code
 ↓
Docker Image
 ↓
Container
 ↓
Deployment
```

---

# 16. TDR-013 — Experiment Tracking

**Decision:** Use MLflow in V2

**Status:** Deferred

## Context

As the project develops, multiple:

- datasets
- feature versions
- models
- hyperparameters
- evaluation results

will need to be tracked.

## Decision

MLflow will be introduced when experiment complexity justifies it.

## Expected Responsibilities

```text
Experiment
    ↓
MLflow Tracking
    ↓
Metrics
    ↓
Artifacts
    ↓
Model
```

Later:

```text
Model
 ↓
Model Registry
 ↓
Deployment
```

## Why Not V1?

V1 should first establish a correct ML pipeline.

MLflow becomes more meaningful once there are real experiments and models to track.

---

# 17. TDR-014 — CI/CD

**Decision:** Use GitHub Actions

**Status:** Deferred

## Context

The project will eventually require automated:

- Testing
- Linting
- Build validation
- Deployment

## Decision

GitHub Actions will be considered for CI/CD.

## Planned Flow

```text
Git Push
   ↓
GitHub Actions
   ├── Tests
   ├── Lint
   ├── Build
   └── Deployment
```

## Why Deferred?

CI/CD should be introduced once there is a stable application that needs automated validation and deployment.

---

# 18. TDR-015 — Explainability

**Decision:** Use SHAP for model explainability where appropriate

**Status:** Deferred

## Context

Users should eventually understand why a model produced a particular output.

## Decision

SHAP will be evaluated for models where its explanations are meaningful.

## Conceptual Flow

```text
Features
   ↓
Model
   ↓
Prediction
   ↓
SHAP
   ↓
Feature Contributions
```

## Important Constraint

SHAP explanations must describe actual model behavior.

They should not be presented as causal explanations unless causality has actually been established.

---

# 19. TDR-016 — RAG

**Decision:** Introduce RAG in V3

**Status:** Deferred

## Context

The platform will eventually need to answer questions requiring information from:

- Financial documents
- Company reports
- Public announcements
- News
- Other textual evidence

## Decision

Use a Retrieval-Augmented Generation architecture.

Conceptually:

```text
Documents
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Store
    ↓
Retriever
    ↓
LLM
    ↓
Answer
```

## Why Not V1?

RAG does not solve the initial V1 requirement.

V1 must first establish:

```text
Data
 ↓
ML
 ↓
Decision Support
```

RAG will be introduced when the platform has useful analytical outputs that can benefit from textual evidence.

---

# 20. TDR-017 — Vector Database

**Decision:** Defer exact vector database selection

**Status:** Deferred

## Context

V3 will require vector search for RAG.

Potential options include:

- pgvector with PostgreSQL
- Qdrant
- Weaviate
- Milvus
- Other managed vector stores

## Decision

Do not select the vector database until the RAG requirements are defined.

## Reasoning

The project should avoid introducing another database unnecessarily.

If PostgreSQL + pgvector satisfies the requirements, using the existing database may provide a simpler architecture.

A dedicated vector database should be selected only if its capabilities provide a meaningful advantage.

---

# 21. TDR-018 — LLM Integration

**Decision:** Use an LLM API or appropriate model in V3

**Status:** Deferred

## Context

The platform will eventually require natural-language explanations and evidence synthesis.

## Decision

The LLM should be introduced only after:

- ML outputs are stable
- Explainability exists
- Evidence retrieval exists

The LLM should synthesize information rather than replace numerical ML models.

## Conceptual Flow

```text
ML Result
    +
SHAP Explanation
    +
Retrieved Evidence
    ↓
LLM
    ↓
Natural-Language Explanation
```

---

# 22. TDR-019 — Agentic AI

**Decision:** Introduce tool-based agentic architecture in V4

**Status:** Deferred

## Context

An AI assistant may eventually need to perform multiple operations:

- Retrieve market data
- Run analytics
- Retrieve forecasts
- Explain predictions
- Search documents
- Inspect monitoring information

## Decision

Use tool calling and orchestration rather than immediately implementing a multi-agent system.

Conceptually:

```text
User
 ↓
Decision Agent
 ├── Forecast Tool
 ├── Analytics Tool
 ├── Explainability Tool
 ├── RAG Tool
 └── Monitoring Tool
```

## Why Not Multi-Agent Immediately?

Multiple agents introduce:

- More complexity
- More communication paths
- More failure modes
- More difficult evaluation

A single orchestrator with well-designed tools should be the starting point.

Multi-agent architecture will only be introduced if there is a demonstrated need.

---

# 23. TDR-020 — Monitoring

**Decision:** Introduce monitoring in V2

**Status:** Deferred

## Context

A deployed ML system must be observable.

Monitoring will eventually cover:

### Data

- Freshness
- Missing values
- Schema changes
- Drift

### Model

- Prediction drift
- Performance
- Error distribution

### Application

- Latency
- Errors
- Request volume

## Decision

The monitoring stack will be selected after deployment architecture is defined.

The system should not adopt multiple monitoring tools simply for demonstration purposes.

---

# 24. TDR-021 — Cloud Platform

**Decision:** Cloud provider not yet finalized

**Status:** Deferred

## Context

The platform will eventually require deployment.

Potential providers include:

- AWS
- Azure
- GCP

## Decision

The cloud provider will be selected based on:

- Internship relevance
- Deployment requirements
- Cost
- Available services
- Learning value
- Integration with the selected architecture

## Important Consideration

Because some target internship roles explicitly mention AWS while others use Azure/Databricks, cloud selection should be made strategically rather than arbitrarily.

---

# 25. TDR-022 — Stream Processing

**Decision:** Do not introduce Kafka initially

**Status:** Accepted for V1

## Context

Financial data can arrive continuously, but the initial V1 system uses daily market data.

## Decision

V1 will use scheduled/batch ingestion.

Conceptually:

```text
Schedule
   ↓
API
   ↓
Ingestion
   ↓
Database
```

## Why Not Kafka?

Kafka is useful for high-throughput event streaming.

V1 does not have that requirement.

Introducing Kafka would add infrastructure without providing meaningful V1 value.

## Future Consideration

Kafka or another streaming technology may be reconsidered if the platform later supports:

- High-frequency data
- Real-time event processing
- Multiple consumers
- Large-scale streaming pipelines

---

# 26. TDR-023 — Microservices

**Decision:** Start with a modular monolith

**Status:** Accepted for V1

## Context

The platform contains several logical components:

- Data ingestion
- ML
- Analytics
- API
- Database

It may be tempting to deploy each as a separate microservice.

## Decision

V1 will use a modular architecture within a single application/deployment boundary.

Conceptually:

```text
                 Backend Application
                        │
        ┌───────────────┼────────────────┐
        │               │                │
    Ingestion        Analytics           ML
        │               │                │
        └───────────────┼────────────────┘
                        │
                    Database
```

## Why?

The project is initially small enough that microservices would add unnecessary:

- deployment complexity
- networking
- observability
- configuration
- testing overhead

The internal module boundaries should nevertheless be designed cleanly.

## Future Consideration

Services may be separated if:

- scaling requirements differ,
- deployment independence becomes necessary,
- teams need independent ownership,
- or system complexity genuinely requires it.

---

# 27. TDR-024 — Frontend Data Visualization

**Decision:** Select charting library during frontend implementation

**Status:** Deferred

## Context

The dashboard will need:

- Price charts
- Volume charts
- Forecast visualizations
- Anomaly indicators
- Model metrics

## Decision

The charting library will be selected after the API data contracts are defined.

Potential options include:

- Recharts
- Plotly
- Apache ECharts

The final decision should consider:

- React integration
- Interactivity
- Time-series support
- Maintainability
- Performance

---

# 28. TDR-025 — Authentication

**Decision:** Defer authentication until required

**Status:** Deferred

## Context

Local V1 development does not require user authentication.

## Decision

Authentication will not be implemented solely for demonstration.

It will be introduced when the deployed application requires:

- User accounts
- Protected endpoints
- Personalized data
- Role-based access

Potential approaches will be evaluated at that stage.

---

# 29. TDR-026 — API Versioning

**Decision:** Use versioned API routes when the public API becomes stable

**Status:** Proposed

## Context

The backend API will evolve as capabilities are added.

## Proposed Approach

Example:

```text
/api/v1/assets
/api/v1/market-data
/api/v1/predictions
```

Future breaking changes could use:

```text
/api/v2/...
```

The exact convention will be finalized during API design.

---

# 30. TDR-027 — Configuration and Secrets

**Decision:** Use environment-based configuration

**Status:** Accepted

## Context

The application will require:

- API keys
- Database credentials
- Environment configuration

## Decision

Secrets will not be hardcoded into source code.

Development configuration may use environment variables.

Example:

```text
DATABASE_URL=...
MARKET_DATA_API_KEY=...
```

A `.env` file containing secrets must not be committed to Git.

A safe example configuration file may be included.

---

# 31. TDR-028 — Documentation Format

**Decision:** Use Markdown

**Status:** Accepted

## Context

The project requires:

- PRD
- Architecture
- Technology decisions
- Database design
- API documentation
- Roadmap
- Interview documentation

## Decision

Markdown will be used for repository documentation.

## Reasoning

Markdown provides:

- Git compatibility
- GitHub rendering
- Easy version control
- Simple editing
- Readability

---

# 32. TDR-029 — Repository Architecture

**Decision:** Use a modular repository structure

**Status:** Accepted

## Initial Structure

```text
decision-intelligence-platform/
│
├── docs/
│   ├── PRD.md
│   ├── SYSTEM_ARCHITECTURE.md
│   └── TECHNOLOGY_DECISION_RECORDS.md
│
├── README.md
│
└── .gitignore
```

As implementation begins:

```text
decision-intelligence-platform/
│
├── backend/
├── frontend/
├── ml/
├── data/
├── database/
├── tests/
├── scripts/
├── docs/
├── README.md
└── .gitignore
```

Additional directories should only be introduced when their functionality is actually implemented.

---

# 33. Technology Stack Summary

## V1

| Area | Technology | Status |
|---|---|---|
| Programming | Python | Accepted |
| Data Processing | Pandas | Accepted |
| Numerical Computing | NumPy | Accepted |
| ML | Scikit-learn | Accepted |
| Gradient Boosting | XGBoost | Candidate |
| Backend | FastAPI | Accepted |
| Database | PostgreSQL | Accepted |
| Frontend | React | Accepted |
| Frontend Language | TypeScript | Accepted |
| Testing | Pytest | Accepted |
| Version Control | Git | Accepted |
| Repository | GitHub | Accepted |
| Market Data | Provider TBD | Pending |

---

# 34. Future Technology Stack

## V2

| Area | Technology | Status |
|---|---|---|
| Experiment Tracking | MLflow | Deferred |
| Model Registry | MLflow | Deferred |
| Containerization | Docker | Deferred |
| CI/CD | GitHub Actions | Deferred |
| Monitoring | TBD | Deferred |
| Cloud | TBD | Deferred |

## V3

| Area | Technology | Status |
|---|---|---|
| Explainability | SHAP | Deferred |
| Embeddings | TBD | Deferred |
| Vector Search | TBD | Deferred |
| RAG | Retrieval + LLM | Deferred |
| LLM | TBD | Deferred |
| LLM Evaluation | TBD | Deferred |

## V4

| Area | Technology | Status |
|---|---|---|
| Tool Calling | LLM tool calling | Deferred |
| Agent Orchestration | TBD | Deferred |
| Multi-Agent System | Conditional | Deferred |

---

# 35. Technology Selection Matrix

The following matrix summarizes the major decisions.

| Requirement | Selected Technology | Primary Reason |
|---|---|---|
| Programming | Python | ML + AI + backend ecosystem |
| Data Processing | Pandas | Strong tabular/time-series ecosystem |
| Numerical Computing | NumPy | Numerical foundation |
| ML | Scikit-learn | Evaluation + preprocessing + ML |
| Boosting | XGBoost | Strong candidate for tabular features |
| Backend | FastAPI | API + validation + Python integration |
| Frontend | React | Production-oriented UI |
| Frontend Types | TypeScript | Type safety |
| Database | PostgreSQL | Relational + production ecosystem |
| Testing | Pytest | Python testing |
| Version Control | Git | Standard source control |
| Repository | GitHub | Collaboration + CI/CD |
| Experiment Tracking | MLflow | MLOps lifecycle |
| Explainability | SHAP | Model interpretation |
| Containerization | Docker | Reproducible deployment |
| CI/CD | GitHub Actions | Repository integration |
| RAG | TBD | Requirements not finalized |
| Vector DB | TBD | Requirements not finalized |
| LLM | TBD | Requirements not finalized |
| Agent Framework | TBD | Requirements not finalized |
| Cloud | TBD | Deployment requirements not finalized |

---

# 36. Decisions That Should NOT Be Made Yet

The following technologies should remain undecided until their requirements are clearer:

- Exact market-data provider
- Exact forecasting algorithm
- Exact vector database
- LLM provider
- Agent framework
- Cloud provider
- Monitoring platform
- Authentication provider
- Frontend charting library

These decisions should be made when the corresponding design problem is reached.

---

# 37. Reconsideration Triggers

Technology decisions should be revisited when one of the following occurs:

### Performance Problem

The current technology cannot satisfy performance requirements.

### Scale Problem

The dataset or workload becomes too large for the current architecture.

### Reliability Problem

The current solution causes unacceptable failures.

### Operational Problem

Deployment or maintenance becomes unnecessarily difficult.

### New Product Requirement

A new capability requires a different technology.

### Better Strategic Fit

A different technology provides significantly stronger value for the target engineering environment.

---

# 38. Final Architecture Philosophy

The project should follow:

```text
Requirement
    ↓
Problem
    ↓
Possible Solutions
    ↓
Trade-off Analysis
    ↓
Technology Decision
    ↓
Implementation
    ↓
Evaluation
    ↓
Reconsideration if Necessary
```

Technology should therefore be a consequence of engineering requirements rather than the starting point.

---

# 39. Current Status

**Technology Decision Records Version:** 0.1  
**Status:** Draft

Completed:

- Programming language decision
- Data-processing decision
- ML framework decision
- Backend decision
- Frontend decision
- Database decision
- Data-provider architecture decision
- Validation architecture decision
- Testing decision
- Version-control decision
- Containerization direction
- MLOps direction
- CI/CD direction
- Explainability direction
- RAG direction
- Agentic AI direction
- Monitoring direction
- Cloud direction
- Streaming decision
- Microservices decision
- Configuration strategy
- Documentation strategy
- Repository strategy

Pending:

- Exact Indian market-data provider
- Exact ML forecasting target
- Exact forecasting model
- Database schema
- API contract
- Cloud deployment strategy
- RAG vector database
- LLM provider
- Agent orchestration framework
- Monitoring stack

Next design document:

> **Database Design Document**