# Architecture Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Users / Clients                                │
│                   (Web Browser, Mobile Apps, API Clients)                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTPS
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CDN (CloudFront)                                 │
│                     (Static assets, Edge caching)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Application Load Balancer (ALB)                        │
│          SSL Termination, Health Checks, Routing, Auto-scaling              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       │                             │
                       ▼                             ▼
        ┌──────────────────────────┐  ┌──────────────────────────┐
        │  FastAPI Instance 1      │  │  FastAPI Instance N      │
        │  ┌────────────────────┐  │  │  ┌────────────────────┐  │
        │  │ Forecast Service   │  │  │  │ Forecast Service   │  │
        │  │ Data Service       │  │  │  │ Data Service       │  │
        │  │ ML Model (v3.0.0) │  │  │  │ ML Model (v3.0.0) │  │
        │  └────────────────────┘  │  │  └────────────────────┘  │
        └──────────────────────────┘  └──────────────────────────┘
                       │                             │
                       └──────────────┬──────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌──────────────┐           ┌──────────────────┐          ┌─────────────────┐
│    Redis     │           │   ML Model       │          │   PostgreSQL    │
│   Cluster    │           │   Service        │          │    Primary      │
│              │           │                  │          │                 │
│ - Forecasts  │           │  ┌────────────┐  │          │  - Sales Data   │
│ - Sessions   │           │  │  XGBoost   │  │          │  - Products     │
│ - Rate Limit │           │  │ Holt-      │  │          │  - Categories   │
│              │           │  │ Winters    │  │          │  - Metadata     │
└──────────────┘           │  │  Ensemble  │  │          └─────────────────┘
                           │  └────────────┘  │                   │
                           │         │         │                   │
                           │         ▼         │                   ▼
                           │  ┌────────────┐  │          ┌─────────────────┐
                           │  │  Feature   │  │          │   PostgreSQL    │
                           │  │   Store    │  │          │   Read Replica  │
                           │  └────────────┘  │          └─────────────────┘
                           └──────────────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        │                           │
                        ▼                           ▼
            ┌──────────────────┐        ┌──────────────────────┐
            │   Data Lake      │        │   External APIs      │
            │     (S3)         │        │   (Future)           │
            │                  │        │                      │
            │ - Raw Data       │        │  - FRED (Economic)   │
            │ - Models         │        │  - Yahoo Finance     │
            │ - Training Data  │        │  - Weather APIs      │
            │ - Backups        │        │                      │
            └──────────────────┘        └──────────────────────┘
```

## Data Flow - Training Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                    Data Generation / Ingestion                    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Synthetic Data Service                         │
│                                                                  │
│  - 8 categories with specific base sales                        │
│  - Seasonal patterns (monthly, weekly)                          │
│  - Weekend effects                                              │
│  - Random noise for realism                                     │
│  - np.random.seed(42) for reproducibility                       │
│  - 2 years of daily data = 5,848 records (730 days)             │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Feature Engineering                          │
│                                                                  │
│  - Time features (day_of_week, month, quarter, etc.)  [6]      │
│  - Lag features (lag_7, lag_14, lag_30)                [3]      │
│  - Rolling stats (mean_7, mean_30, std_7, std_30)     [4]      │
│  - Category encoding                                   [1]      │
│  - Cyclical encoding (sin/cos), trend, momentum, interaction    │
│  - Total: 25 features                                           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Model Training                              │
│                                                                  │
│  ┌────────────────┐                  ┌────────────────┐         │
│  │    XGBoost     │                  │  Holt-Winters  │         │
│  │   Training     │                  │   Training     │         │
│  │                │                  │                │         │
│  │ - All cats     │                  │ - Per category │         │
│  │ - 25 features  │                  │ - Weekly seas. │         │
│  │ - 500 trees    │                  │ - period=7     │         │
│  └────────────────┘                  └────────────────┘         │
│          │                                    │                 │
│          └────────────────┬───────────────────┘                 │
│                           ▼                                     │
│                  ┌─────────────────┐                            │
│                  │ Ensemble Model  │                            │
│                  │ 60% XGB + 40%  │                            │
│                  │ Holt-Winters    │                            │
│                  └─────────────────┘                            │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Model Evaluation                            │
│                                                                  │
│  - Holdout: last 30 days                                        │
│  - Metrics: MAE, RMSE, R²                                      │
│  - XGBoost Train R²: 0.999, Val R²: 0.978                       │
│  - Holdout R²: 0.96, MAE: 4.1%, MAPE: 4.3%                      │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│               Model Artifact Storage                             │
│                                                                  │
│  - ensemble_model.pkl (joblib)                                  │
│  - Contains: XGBoost model, Holt-Winters models,               │
│    feature columns, scaler                                       │
│  - Loaded by ForecastService at startup                         │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow - Prediction Request

```
┌──────────────┐
│    Client    │
│  (Browser)   │
└──────────────┘
       │
       │ GET /api/v1/forecast/top-products?time_period=month&category=Electronics
       │
       ▼
┌──────────────────────────────────────────┐
│         Load Balancer                    │
└──────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│        FastAPI Service                   │
│                                          │
│  1. Request Validation (Pydantic v2)     │
│  2. Route to Forecast Service            │
└──────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│      Forecast Service                    │
│                                          │
│  1. Load ensemble model (if not cached)  │
│  2. Generate synthetic historical data   │
│  3. Call model.predict()                 │
│     - XGBoost: 25-feature prediction    │
│     - Holt-Winters: seasonal forecast   │
│     - Ensemble: 60/40 weighted avg      │
│  4. Post-process: confidence intervals   │
└──────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Return Response                         │
│                                          │
│  {                                       │
│    products: [...],                      │
│    model_version: "3.0.0",              │
│    accuracy_score: 0.96                 │
│  }                                       │
└──────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│    React Dashboard                       │
│                                          │
│  - Intuit-themed UI                      │
│  - Recharts for visualization            │
│  - WCAG accessible                       │
│  - Keyboard navigation                   │
└──────────────────────────────────────────┘
```

## Deployment Architecture (AWS - Production Design)

```
┌────────────────────────────────────────────────────────────────────┐
│                          Route 53 (DNS)                            │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                      CloudFront (CDN)                              │
│                   - Global edge locations                          │
│                   - Static React build served                      │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                  WAF (Web Application Firewall)                    │
│                   - SQL injection protection                       │
│                   - XSS protection                                 │
│                   - Rate limiting                                  │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                     VPC (Virtual Private Cloud)                    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              Public Subnets (Multi-AZ)                       │ │
│  │  ┌──────────────────┐        ┌──────────────────┐           │ │
│  │  │  ALB (AZ-1)      │        │  ALB (AZ-2)      │           │ │
│  │  │  NAT Gateway     │        │  NAT Gateway     │           │ │
│  │  └──────────────────┘        └──────────────────┘           │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                │                                   │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              Private Subnets (Multi-AZ)                      │ │
│  │                                                              │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │           Application Tier (Auto Scaling)            │   │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │ │
│  │  │  │ FastAPI  │  │ FastAPI  │  │ FastAPI  │ ...       │   │ │
│  │  │  │  EC2/ECS │  │  EC2/ECS │  │  EC2/ECS │           │   │ │
│  │  │  │  + Model │  │  + Model │  │  + Model │           │   │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘           │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  │                                                              │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │                  Data Tier                           │   │ │
│  │  │  ┌──────────────┐         ┌──────────────┐          │   │ │
│  │  │  │ ElastiCache  │         │     RDS      │          │   │ │
│  │  │  │   (Redis)    │         │ (PostgreSQL) │          │   │ │
│  │  │  │   Cluster    │         │  Multi-AZ    │          │   │ │
│  │  │  └──────────────┘         └──────────────┘          │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                          External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │      S3      │  │  CloudWatch  │  │   Parameter  │            │
│  │   (Models,   │  │   (Logs,     │  │    Store     │            │
│  │    Data)     │  │   Metrics)   │  │   (Secrets)  │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└────────────────────────────────────────────────────────────────────┘
```

## Monitoring & Observability Stack

```
┌────────────────────────────────────────────────────────────────┐
│                     Application Logs                           │
│         (FastAPI + loguru, Model Service, Workers)             │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                   Log Aggregation                              │
│               (CloudWatch Logs / ELK Stack)                    │
│                                                                │
│  - Structured JSON logs                                        │
│  - Log parsing and indexing                                    │
│  - Full-text search                                            │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                  Metrics Collection                            │
│              (CloudWatch / Prometheus)                         │
│                                                                │
│  - Application: Request rate, latency, errors                  │
│  - Infrastructure: CPU, memory, disk, network                  │
│  - Business: Prediction accuracy, model version                │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                     Visualization                              │
│                 (Grafana / CloudWatch)                         │
│                                                                │
│  - Real-time dashboards                                        │
│  - Model performance tracking                                  │
│  - Business KPIs                                               │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                      Alerting                                  │
│                 (PagerDuty / SNS / Slack)                      │
│                                                                │
│  - Threshold-based alerts                                      │
│  - Model drift detection                                       │
│  - On-call rotation                                            │
└────────────────────────────────────────────────────────────────┘
```
