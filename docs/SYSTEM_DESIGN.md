# QuickBooks Commerce Sales Forecasting System - System Design

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Architecture](#architecture)
4. [Component Design](#component-design)
5. [Data Flow](#data-flow)
6. [ML Model Design](#ml-model-design)
7. [API Design](#api-design)
8. [Scalability & Performance](#scalability--performance)
9. [Security](#security)
10. [Monitoring & Observability](#monitoring--observability)

## Overview

The QuickBooks Commerce Sales Forecasting System is designed to predict top-selling products by category across different time periods (week, month, year) to help merchants optimize inventory and business strategy.

### Key Objectives
- **Accuracy**: Achieve >80% prediction accuracy (R²)
- **Availability**: 99.9% uptime SLA (production design)
- **Scalability**: Handle 10K+ requests per minute (production design)
- **Latency**: < 500ms response time for predictions

## Requirements

### Functional Requirements
1. **FR1**: Predict sales by category for selectable time periods (week, month, year)
2. **FR2**: Display top N products per category with predicted sales volumes
3. **FR3**: Show confidence intervals and trend indicators
4. **FR4**: Provide accessible, Intuit-branded dashboard UI
5. **FR5**: Support model training pipeline with evaluation metrics

### Non-Functional Requirements
1. **NFR1**: 99.9% availability (High Availability design)
2. **NFR2**: < 500ms latency for forecast requests
3. **NFR3**: Model accuracy R² > 0.80
4. **NFR4**: WCAG AA accessible frontend
5. **NFR5**: Horizontal scalability for compute

### Out of Scope
- Real-time streaming predictions
- Multi-tenant isolation (single-tenant for now)
- Custom model training per user

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Web App    │  │  Mobile App  │  │   API Clients│         │
│  │  (React +    │  │  (Future)    │  │              │         │
│  │  Intuit UI)  │  │              │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Load Balancer (ALB)                        │
│                     (Health checks, SSL termination)            │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│   FastAPI Service        │   │   FastAPI Service        │
│   (Auto-scaling)         │   │   (Auto-scaling)         │
│   - Forecast endpoints   │   │   - Forecast endpoints   │
│   - Ensemble model v2.0  │   │   - Ensemble model v2.0  │
└──────────────────────────┘   └──────────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Redis      │    │   ML Model   │    │  PostgreSQL  │
│   Cache      │    │   Service    │    │  Database    │
│              │    │              │    │              │
│ - Forecasts  │    │ - XGBoost    │    │ - Sales data │
│ - Sessions   │    │ - Holt-      │    │ - Metadata   │
└──────────────┘    │   Winters    │    │ - Users      │
                    │ - Ensemble   │    └──────────────┘
                    └──────────────┘
```

### Architecture Components

#### 1. **Presentation Layer**
- React SPA with TypeScript
- Intuit/QuickBooks brand theme (CSS variables)
- WCAG AA accessible (ARIA, keyboard nav, focus styles)
- Recharts for data visualization

#### 2. **API Layer**
- FastAPI (Python) for high-performance async operations
- RESTful endpoints
- OpenAPI/Swagger documentation (auto-generated)
- Pydantic v2 request/response validation

#### 3. **Business Logic Layer**
- Forecast service: Orchestrates predictions using trained model
- Data service: Synthetic data generation with category-specific baselines
- Model loading: ensemble_model.pkl loaded at startup

#### 4. **Data Layer (Production Design)**
- **PostgreSQL**: Transactional data (sales, products, users)
- **Redis**: Caching layer for frequent queries
- **S3**: Model artifacts, training data, backups

#### 5. **ML Layer**
- Ensemble model (XGBoost + Holt-Winters)
- 17 engineered features
- Model versioning (currently v2.0.0)
- Training pipeline with holdout evaluation

## Component Design

### 1. API Service (FastAPI)

```python
# Key modules:
- app/api/forecasting.py    # Forecast endpoints
- app/api/data.py           # Data access endpoints
- app/api/health.py         # Health check endpoints
- app/services/forecast_service.py  # Business logic + model inference
- app/models/forecast_model.py      # Ensemble model (XGBoost + Holt-Winters)
```

**Responsibilities:**
- Request validation (Pydantic v2)
- Business logic orchestration
- Model inference
- Response formatting

**Design Patterns:**
- Service layer pattern
- Factory pattern for model loading
- Singleton for model instance

### 2. ML Model Service

```python
# Ensemble approach:
1. XGBoost: Captures complex feature interactions (17 features)
2. Holt-Winters: Handles weekly seasonality per category
3. Ensemble: 60% XGBoost + 40% Holt-Winters weighted average
```

**Model Pipeline:**
1. Data generation (synthetic, reproducible)
2. Feature engineering (17 features)
3. Model training (XGBoost + Holt-Winters)
4. Model evaluation (30-day holdout)
5. Model serialization (joblib → ensemble_model.pkl)
6. Inference (loaded at service startup)

**Feature Engineering:**
- Time features: day_of_week, month, quarter, week_of_year, day_of_month, is_weekend
- Lag features: sales_lag_7, sales_lag_14, sales_lag_30
- Rolling statistics: rolling_mean_7, rolling_mean_30, rolling_std_7, rolling_std_30
- Category encoding

### 3. Caching Strategy (Production Design)

```
Redis Cache Hierarchy:
- L1: Individual product forecasts (TTL: 1 hour)
- L2: Category aggregations (TTL: 30 minutes)
- L3: Model predictions (TTL: 6 hours)
```

**Cache Invalidation:**
- Time-based expiration
- Event-driven invalidation (model retrained)
- Manual invalidation API

## Data Flow

### 1. Training Data Flow

```
Synthetic Data Generation → Feature Engineering → Model Training → Evaluation → Save to disk
     │                           │                    │               │            │
     └─ seed(42)                └─ 17 features       └─ XGBoost     └─ R² 0.82  └─ .pkl
     └─ 8 categories            └─ lag, rolling      └─ Holt-Winters
     └─ 1 year daily                                  └─ Ensemble
     └─ 2,928 records
```

### 2. Prediction Request Flow

```
Client → FastAPI → ForecastService → Load Model (if needed)
                                          │
                                     Model.predict()
                                          │
                                    ┌─────┴─────┐
                                    │           │
                                XGBoost    Holt-Winters
                                    │           │
                                    └─────┬─────┘
                                          │
                                     Ensemble (60/40)
                                          │
                                    Post-process
                                          │
                                      Response
```

## ML Model Design

### Model Architecture

**Ensemble Model Components:**

1. **XGBoost Regressor**
   - Purpose: Capture non-linear patterns across all categories
   - Features: 17 engineered features
   - Hyperparameters: n_estimators=200, max_depth=6, learning_rate=0.05

2. **Holt-Winters (Exponential Smoothing)**
   - Purpose: Time-series seasonality per category
   - Seasonality: Weekly (period=7)
   - Trend: Additive
   - One model per category

3. **Ensemble Strategy**
   - Weighted average: 60% XGBoost, 40% Holt-Winters
   - Non-negative constraint on predictions

### Model Performance Metrics

| Metric | Value |
|--------|-------|
| XGBoost Train R² | 0.983 |
| Holdout R² | 0.823 |
| Holdout MAE | ~11% |
| Model Version | 2.0.0 |

## API Design

### Key Endpoints

```yaml
GET /api/v1/forecast/top-products
  Query Parameters:
    - time_period: week|month|year
    - category: string (optional)
    - limit: integer (default: 10)
  Response:
    - products: ProductForecast[]
    - total_count: integer
    - generated_at: timestamp

GET /api/v1/forecast/categories
  Query Parameters:
    - time_period: week|month|year
  Response:
    - predictions: CategoryForecast[]
    - model_version: "2.0.0"
    - accuracy_score: 0.82

GET /api/v1/forecast/trends/{category}
  Path Parameters:
    - category: string
  Query Parameters:
    - days: integer (default: 90)
  Response:
    - historical_data: TrendDataPoint[]
    - forecast_data: TrendDataPoint[]
    - statistics: object (mean, min, max, trend)

POST /api/v1/forecast/predict
  Request Body:
    - time_period: string
    - categories: string[]
    - include_confidence: boolean
  Response:
    - forecast_date: timestamp
    - predictions: CategoryForecast[]
    - model_version: "2.0.0"
```

## Scalability & Performance

### Horizontal Scaling Strategy (Production Design)

1. **API Layer**
   - Auto-scaling groups (2-20 instances)
   - Scale based on CPU (> 70%) or Request Count
   - Health checks every 30 seconds
   - Each instance loads model into memory at startup

2. **Database Layer**
   - Read replicas for query distribution
   - Partitioning by date
   - Connection pooling

3. **Cache Layer**
   - Redis cluster (3-5 nodes)
   - Consistent hashing for distribution

### Performance Optimization

1. **Model Loading**: Load once at startup, keep in memory
2. **Response Compression**: GZIP for API responses
3. **Asynchronous Processing**: FastAPI async/await
4. **Feature Computation**: Efficient pandas/numpy operations

## Security

### Authentication & Authorization (Production Design)

```
1. API Key Authentication
   - Rate limiting per API key
   - Key rotation every 90 days

2. OAuth 2.0 (Future)
   - Integration with QuickBooks SSO
   - JWT tokens

3. Role-Based Access Control
   - Admin: Full access
   - Merchant: Read-only access to their data
```

### Data Security

1. **Encryption**: At rest (AES-256), In transit (TLS 1.3)
2. **PII Protection**: Anonymize customer data, GDPR compliance
3. **Network Security**: VPC with private subnets, WAF

## Monitoring & Observability

### Metrics

1. **Application Metrics**: Request rate, latency, error rate
2. **Model Metrics**: Prediction accuracy, model version, inference time
3. **Infrastructure Metrics**: CPU, memory, disk usage

### Logging

```
Log Levels:
- ERROR: System failures, exceptions
- WARN: Degraded performance, model fallbacks
- INFO: Key business events, predictions served
- DEBUG: Detailed execution flow

Library: loguru (structured logging)
```

### Alerting

```yaml
Critical Alerts:
  - API error rate > 5%
  - Model not loaded / prediction failure
  - Database connection pool exhausted

Warning Alerts:
  - Model accuracy drift detected
  - CPU usage > 80%
  - High response latency
```

## Future Enhancements

1. **Real-time Predictions**: Stream processing with Kafka
2. **External Data**: Integrate FRED API, Yahoo Finance
3. **Advanced ML**: LSTM, Transformer models
4. **Multi-tenancy**: Tenant isolation and resource quotas
5. **Mobile Apps**: Native iOS and Android apps
6. **Advanced Analytics**: Anomaly detection, causal analysis

## Conclusion

This system design provides a scalable, accessible, and accurate sales forecasting solution:
- Trained ensemble model (XGBoost + Holt-Winters) with R² 0.82
- FastAPI backend with auto-generated docs
- Intuit-themed, WCAG-accessible React frontend
- Production-ready architecture design (AWS)
- Comprehensive monitoring and observability plan
