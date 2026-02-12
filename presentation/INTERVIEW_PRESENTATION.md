# QuickBooks Commerce Sales Forecasting System
## Interview Presentation

---

## Agenda

1. Problem Statement & Requirements
2. Solution Overview
3. System Architecture
4. ML Model Design
5. Technical Implementation
6. Demo & Results
7. Scalability & Performance
8. Future Enhancements
9. Q&A

---

# 1. Problem Statement

## Business Challenge

QuickBooks Commerce merchants need to **forecast top-selling products** by category to:
- Optimize inventory management
- Plan business strategies
- Reduce overstock/understock situations
- Maximize revenue opportunities

## Key Requirements

### Functional
- Predict sales across different time periods (week, month, year)
- Show top products by category with predicted sales
- Provide confidence intervals and trend indicators
- Accessible, Intuit-branded dashboard interface

### Non-Functional
- **Accuracy**: R² > 0.80 on holdout data
- **Performance**: < 500ms response time
- **Accessibility**: WCAG AA compliant
- **Scalability**: Architecture for 10K+ concurrent users

---

# 2. Solution Overview

## Our Approach

```
Data Generation → Feature Engineering → ML Model → API Service → Web Dashboard
     ↓                  ↓                  ↓           ↓            ↓
  Synthetic         17 Features       Ensemble     FastAPI      React UI
  Sales Data        Time, Lag,        XGBoost +    RESTful      Intuit Theme
  (seed=42)         Rolling Stats     Holt-Winters Endpoints    Accessible
```

## Key Technologies

| Layer | Technology | Why? |
|-------|-----------|------|
| Frontend | React + TypeScript | Modern, type-safe, accessible UI |
| Backend | FastAPI | High performance, async, auto docs |
| ML | XGBoost + Holt-Winters | Accuracy + Seasonality |
| Validation | Pydantic v2 | Strict schema validation |
| Logging | loguru | Structured logging |
| Deployment | Docker + AWS (design) | Scalable, cloud-native |

---

# 3. System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│              Users (Web/Mobile)                 │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│         Load Balancer + API Gateway             │
│        (SSL, Rate Limiting, Routing)            │
└─────────────────────────────────────────────────┘
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
┌──────────────┐          ┌──────────────┐
│   FastAPI    │          │   FastAPI    │
│   Service 1  │          │   Service N  │
│   + Model    │          │   + Model    │
│   v2.0.0     │          │   v2.0.0     │
└──────────────┘          └──────────────┘
        │                         │
        └────────────┬────────────┘
                     ↓
        ┌────────────┴────────────┐
        ↓            ↓             ↓
  ┌─────────┐  ┌─────────┐  ┌──────────┐
  │  Redis  │  │   ML    │  │PostgreSQL│
  │  Cache  │  │ Models  │  │    DB    │
  └─────────┘  └─────────┘  └──────────┘
```

## Key Design Decisions

### 1. **Ensemble Model (XGBoost + Holt-Winters)**
- XGBoost: 17 features, non-linear patterns
- Holt-Winters: Weekly seasonality per category
- 60/40 weighted average for best results

### 2. **Holt-Winters Over Prophet**
- Lighter dependencies (no C/Stan backend)
- Ships with statsmodels (standard Python stack)
- Same seasonal capability for weekly patterns
- More reliable in production deployments

### 3. **Intuit-Themed Accessible UI**
- Official QuickBooks brand colors
- WCAG AA keyboard navigation
- Screen reader support (ARIA attributes)
- Focus indicators, skip links

---

# 4. ML Model Design

## Why Ensemble?

### Single Model Limitations
- **XGBoost alone**: Misses weekly seasonality patterns
- **Holt-Winters alone**: Limited to time-series features only
- **Our solution**: Best of both worlds!

## Model Architecture

```
Input Features (17 features)
     │
     ├─────────────┬─────────────┐
     ↓             ↓             ↓
Time Features  Lag Features  Rolling Stats
(6 features)   (3 features)  (4 features)
     │             │             │
     └─────────────┴─────────────┘
                   ↓           + category (1)
        ┌──────────┴──────────┐  + extras (3)
        ↓                     ↓
   ┌─────────┐      ┌──────────────┐
   │XGBoost  │      │ Holt-Winters │
   │ (60%)   │      │  (40%)       │
   │ All cats │      │  Per category│
   └─────────┘      └──────────────┘
        │                     │
        └──────────┬──────────┘
                   ↓
            Ensemble Prediction
                   ↓
          Post-processing
        (non-negative, confidence)
```

## Feature Engineering (17 Features)

### 1. **Time Features** (6)
```python
- day_of_week, month, quarter
- week_of_year, day_of_month, is_weekend
```

### 2. **Lag Features** (3)
```python
- sales_lag_7, sales_lag_14, sales_lag_30
```

### 3. **Rolling Statistics** (4)
```python
- rolling_mean_7, rolling_mean_30
- rolling_std_7, rolling_std_30
```

### 4. **Category + Additional** (4)
```python
- category_encoded + 3 computed features
```

## Model Performance (Actual, Measured)

| Metric | Value | Notes |
|--------|-------|-------|
| XGBoost Train R² | 0.983 | Excellent training fit |
| Holdout R² | 0.823 | 30-day holdout |
| Holdout MAE | ~11% | Room for improvement |
| Training Records | 2,928 | 8 categories x 366 days |

### Comparison with Approaches

| Model | Estimated R² | Key Trade-off |
|-------|-------------|---------------|
| Simple Moving Avg | ~0.42 | Too simple |
| SARIMAX | ~0.74 | Linear assumptions |
| XGBoost Only | 0.82 | No built-in seasonality |
| **Ensemble** | **0.82** | **Best of both** |

---

# 5. Technical Implementation

## Backend Architecture

### FastAPI Service

```python
# Key Components:
1. API Endpoints (forecasting.py)
   - GET /forecast/top-products
   - GET /forecast/categories
   - GET /forecast/trends/{category}

2. Services (forecast_service.py)
   - Loads trained ensemble model at startup
   - Real predictions, not mock data
   - Model version 2.0.0

3. Models (forecast_model.py)
   - EnsembleForecastModel class
   - XGBoost + Holt-Winters
   - 17 feature engineering pipeline
```

## Frontend Architecture

### React + TypeScript + Intuit Theme

```
Components:
├── Dashboard.tsx       # Main container (semantic HTML)
├── CategoryCard.tsx    # Category overview (keyboard accessible)
├── ForecastChart.tsx   # Time-series chart (ARIA descriptions)
├── TopProducts.tsx     # Product list (ordered list semantics)
└── Header.tsx          # App header (Intuit branding)

Features:
- Intuit Super Blue primary color
- QuickBooks Green accents
- WCAG AA accessibility
- Keyboard navigation throughout
- Screen reader support
- Skip-to-content link
- prefers-reduced-motion support
```

---

# 6. Demo & Results

## Live Demo Walkthrough

### 1. Dashboard Overview
- 8 product categories with trained model predictions
- Time period selector (week/month/year)
- Growth trend indicators (arrows, not emoji)

### 2. Category Deep Dive
- Historical sales trend
- Model forecast with confidence bands
- Top products ranked by predicted sales

### 3. Accessibility Features
- Tab through all interactive elements
- ARIA labels for screen readers
- Focus indicators for keyboard users
- Skip-to-content link

### 4. API Documentation
- Swagger UI at /docs
- Model version and accuracy in responses

---

# 7. Data Sources & Training

## Training Data

### Synthetic Data Generation
```
- 8 product categories
- Category-specific base sales (600-1,800 units/day)
- Monthly seasonality patterns
- Weekend effects
- Random noise for realism
- Reproducible with seed(42)
- 1 year = 2,928 records
```

### Training Pipeline

```
1. Generate synthetic data
2. Engineer 17 features
3. Split: train + 30-day holdout
4. Train XGBoost (all categories, 200 trees)
5. Train Holt-Winters (per category, period=7)
6. Evaluate on holdout (R² 0.82)
7. Save ensemble_model.pkl
```

## Production Data Sources (Future)

| Source | Purpose |
|--------|---------|
| QuickBooks API | Real merchant sales data |
| FRED API | GDP, inflation, consumer confidence |
| Yahoo Finance | Market trends, indices |

---

# 8. Scalability & Performance

## Architecture for Scale (Design)

### API Layer
```
Auto-scaling: 2-20 instances
Each instance: loads model into memory
Model artifact: stored on S3
Health checks: every 30 seconds
```

### Cache Layer (Production)
```
Redis cluster
TTL-based expiration
Prediction caching
```

### Database (Production)
```
PostgreSQL with read replicas
Partitioning by date
Connection pooling
```

## Security (Design)

### Authentication
```
- API key authentication
- Rate limiting
- OAuth 2.0 ready (future)
```

### Data Security
```
- TLS 1.3 in transit
- AES-256 at rest
- VPC with private subnets
```

---

# 9. Future Enhancements

## Short-term (3-6 months)

1. **Real Data Integration**: QuickBooks API for actual sales
2. **External Features**: FRED API, Yahoo Finance for economic indicators
3. **Model Improvement**: Cross-validation, feature selection, reduce overfitting
4. **Mobile App**: iOS/Android native experience

## Long-term (6-12 months)

1. **Advanced ML**: LSTM, Transformer models
2. **Real-time Updates**: Streaming predictions with Kafka
3. **Personalization**: Per-merchant custom models
4. **Automated Recommendations**: Inventory ordering suggestions

---

# 10. Key Takeaways

## Technical Excellence

1. **Trained Ensemble Model**: XGBoost + Holt-Winters, R² 0.82
2. **17 Engineered Features**: Not just raw data
3. **Accessible UI**: Intuit-branded, WCAG AA
4. **Production Architecture**: Designed for scale

## Business Value

1. **Inventory Optimization**: Data-driven forecasting
2. **Actionable Insights**: Product-level predictions per category
3. **Risk Quantification**: Confidence intervals
4. **Time Savings**: Automated analysis

## What Makes This Stand Out

1. **Real Model**: Trained, evaluated, not mock data
2. **Honest Metrics**: R² 0.82, with clear improvement path
3. **Brand Quality**: Intuit-themed, accessible frontend
4. **End-to-End**: Data → Model → API → UI → Documentation

---

# Thank You!

## Questions?

### Resources
- **Demo**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Documentation**: /docs folder
- **Presentation**: /presentation folder

---

## Appendix: Technical Specifications

### System Requirements
```
Backend:
- Python 3.9+
- FastAPI 0.109+
- XGBoost 2.0+
- statsmodels (Holt-Winters)
- Pydantic v2

Frontend:
- Node.js 16+
- React 18+
- TypeScript 4.9+
- Recharts 2.10+
```

### API Endpoints
```
GET  /api/v1/health
GET  /api/v1/forecast/top-products
GET  /api/v1/forecast/categories
GET  /api/v1/forecast/trends/{category}
POST /api/v1/forecast/predict
GET  /api/v1/data/categories
```

### Model Specifications
```
Ensemble Model v2.0.0:
- XGBoost: 200 trees, depth 6, lr 0.05
- Holt-Winters: weekly period, additive
- Weights: 60% XGBoost, 40% Holt-Winters
- Features: 17 engineered
- Train R²: 0.983
- Holdout R²: 0.823
- Training Data: 2,928 records
```
