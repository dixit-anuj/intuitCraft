# QuickBooks Commerce Sales Forecasting System
## Complete Project Overview

---

## What You Have

A **production-ready sales forecasting system** built for your Intuit interview that demonstrates:

- Machine Learning (Ensemble XGBoost + Holt-Winters)
- Full-Stack Development (React + FastAPI)
- System Design & Architecture
- Intuit-Themed Accessible UI
- Production-Grade Code
- Comprehensive Documentation

---

## Project Structure

```
IntuitCraft/
├── README.md                    # Project overview
├── QUICK_START.md              # 5-minute setup guide
├── PROJECT_OVERVIEW.md         # This file
├── setup.sh                    # Automated setup script
├── .gitignore                  # Git ignore rules
│
├── backend/                    # Python FastAPI Service
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── health.py         # Health check
│   │   │   ├── forecasting.py   # Forecast endpoints
│   │   │   └── data.py           # Data endpoints
│   │   ├── services/          # Business logic
│   │   │   ├── forecast_service.py  # Uses trained model
│   │   │   └── data_service.py
│   │   ├── models/            # ML models & schemas
│   │   │   ├── forecast_model.py # Ensemble (XGBoost + Holt-Winters)
│   │   │   └── schemas.py        # Pydantic v2 schemas
│   │   ├── core/              # Configuration
│   │   │   └── config.py
│   │   └── main.py               # FastAPI app entry
│   ├── data/models/           # Trained model artifacts
│   │   └── ensemble_model.pkl
│   ├── notebooks/             # Jupyter notebooks
│   │   └── 01_data_exploration.ipynb
│   ├── scripts/               # Utility scripts
│   │   └── train_model.py
│   ├── requirements.txt          # Python dependencies
│   └── .env.example             # Environment template
│
├── frontend/                   # React TypeScript UI
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Header.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── CategoryCard.tsx
│   │   │   ├── ForecastChart.tsx
│   │   │   └── TopProducts.tsx
│   │   ├── services/          # API client
│   │   │   └── api.ts
│   │   ├── App.tsx              # Main app
│   │   └── index.tsx            # Entry point
│   ├── public/
│   │   └── index.html
│   ├── package.json             # Node dependencies
│   └── tsconfig.json            # TypeScript config
│
├── docs/                      # Documentation
│   ├── SYSTEM_DESIGN.md         # Detailed system design
│   ├── ARCHITECTURE_DIAGRAM.md  # Architecture diagrams
│   ├── ML_MODEL_DETAILS.md      # ML model documentation
│   ├── MODEL_COMPARISON.md      # Model comparison analysis
│   └── SARIMAX_ANALYSIS.md      # Classical model analysis
│
└── presentation/              # Interview materials
    ├── INTERVIEW_PRESENTATION.md # Full presentation
    ├── DEMO_SCRIPT.md           # Step-by-step demo guide
    └── KEY_METRICS.md           # Performance metrics
```

---

## Quick Start (5 Minutes)

### Option 1: Automated Setup

```bash
cd /Users/anujdixit/Desktop/IntuitCraft
./setup.sh
```

### Option 2: Manual Setup

**Terminal 1 - Backend:**
```bash
cd /Users/anujdixit/Desktop/IntuitCraft/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m scripts.train_model   # Train the model first
python -m app.main
```

**Terminal 2 - Frontend:**
```bash
cd /Users/anujdixit/Desktop/IntuitCraft/frontend
npm install
npm start
```

**Access:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## Documentation Guide

### For Interview Preparation

1. **Start Here**: `QUICK_START.md`
   - Get the demo running
   - Train the model
   - Test all features

2. **System Design**: `docs/SYSTEM_DESIGN.md`
   - Architecture deep dive
   - Technical decisions
   - Scalability approach
   - Security considerations

3. **Presentation**: `presentation/INTERVIEW_PRESENTATION.md`
   - Complete slide deck
   - All talking points
   - Technical explanations
   - Business value

4. **Demo Script**: `presentation/DEMO_SCRIPT.md`
   - Step-by-step walkthrough
   - Exact words to say
   - Q&A preparation
   - Time management

5. **Metrics**: `presentation/KEY_METRICS.md`
   - Performance numbers
   - Business impact
   - Comparisons

### For Technical Deep Dives

6. **ML Model**: `docs/ML_MODEL_DETAILS.md`
   - Feature engineering (17 features)
   - Model architecture (XGBoost + Holt-Winters)
   - Training pipeline
   - Evaluation results

7. **Model Comparison**: `docs/MODEL_COMPARISON.md`
   - 5 approaches evaluated
   - Why ensemble wins
   - SARIMAX analysis

8. **Architecture**: `docs/ARCHITECTURE_DIAGRAM.md`
   - System diagrams
   - Data flow
   - Deployment architecture

---

## Key Features to Demonstrate

### 1. Dashboard Overview
- 8 product categories with trained model predictions
- Time period selection (week/month/year)
- Growth indicators and trend arrows

### 2. Category Deep Dive
- Historical sales trend (60 days)
- Future forecast (30 days) from trained model
- Confidence intervals (95%)
- Statistical summary

### 3. Top Products
- Ranked by predicted sales
- Revenue projections
- Growth percentages
- Trend indicators (up/down/stable arrows)

### 4. API Documentation
- Interactive Swagger UI at /docs
- Try out endpoints live
- Request/response schemas

### 5. Accessibility & Design
- Intuit/QuickBooks brand colors
- WCAG AA keyboard navigation
- Screen reader support (ARIA)
- Focus indicators, skip links

---

## Key Talking Points

### Technical Excellence

1. **Ensemble ML Model**
   - XGBoost + Holt-Winters (Exponential Smoothing)
   - 82% R² on 30-day holdout
   - 17 engineered features
   - Real trained model, not mock data

2. **Production Code Quality**
   - Pydantic v2 schemas with strict validation
   - Structured logging with loguru
   - Error handling throughout
   - RESTful API with auto-generated docs

3. **Accessible Frontend**
   - WCAG AA compliant
   - Intuit brand theme
   - Keyboard navigation
   - Screen reader support

4. **Scalable Architecture**
   - Microservices design
   - Horizontal scaling approach
   - Cache-friendly API design
   - Cloud-native (AWS ready)

### Business Value

1. **Cost Savings**
   - Reduced overstock through data-driven forecasting
   - Better inventory turnover

2. **Revenue Impact**
   - Better inventory of trending items
   - Prevent stockouts on high-demand products

3. **Time Savings**
   - Automated insights replace manual forecasting
   - Data-driven decisions

4. **Merchant Benefits**
   - Easy-to-understand insights
   - Actionable recommendations
   - Confidence in decisions

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **Model R² (holdout)** | 0.82 |
| **XGBoost Train R²** | 0.98 |
| **MAE (holdout)** | 11% |
| **Engineered Features** | 17 |
| **Training Records** | 2,928 |
| **Model Version** | 2.0.0 |
| **Categories** | 8 |

---

## Tech Stack Summary

### Backend
- **Language**: Python 3.9+
- **Framework**: FastAPI (async, high performance)
- **ML**: XGBoost, statsmodels (Holt-Winters), Scikit-learn
- **Data**: Pandas, NumPy
- **Validation**: Pydantic v2
- **API**: RESTful, OpenAPI/Swagger

### Frontend
- **Language**: TypeScript
- **Framework**: React 18
- **Charts**: Recharts
- **HTTP**: Axios
- **Styling**: Custom CSS with Intuit brand variables
- **Accessibility**: WCAG AA, ARIA, keyboard navigation

### Infrastructure (Production Design)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Deployment**: Docker, AWS
- **Monitoring**: CloudWatch, Grafana

---

## Demo Checklist

### Before the Interview

- [ ] Train the model: `python -m scripts.train_model`
- [ ] Test backend starts successfully: `python -m app.main`
- [ ] Test frontend loads and displays data: `npm start`
- [ ] Check all API endpoints at http://localhost:8000/docs
- [ ] Verify charts render with model data
- [ ] Test time period switching
- [ ] Test category selection and keyboard navigation
- [ ] Practice the demo flow 3 times

### During Demo

- [ ] Start with problem statement
- [ ] Show dashboard overview
- [ ] Drill into a category, show chart
- [ ] Explain ML model approach (XGBoost + Holt-Winters)
- [ ] Discuss scalability design
- [ ] Show API documentation
- [ ] Mention accessibility features
- [ ] Conclude with business impact
- [ ] Be ready for Q&A

---

## Common Issues & Solutions

### Backend Won't Start

```bash
python3 --version  # Should be 3.9+

cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Model Not Found

```bash
cd backend
source venv/bin/activate
python -m scripts.train_model
```

### Frontend Won't Start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use

```bash
lsof -i :8000 -t | xargs kill
# Or change frontend port:
PORT=3001 npm start
```

---

## API Endpoints

```
GET  /api/v1/health
GET  /api/v1/forecast/top-products
GET  /api/v1/forecast/categories
GET  /api/v1/forecast/trends/{category}
POST /api/v1/forecast/predict
GET  /api/v1/data/categories
```

### Key Commands
```bash
# Train model
cd backend && source venv/bin/activate && python -m scripts.train_model

# Start backend
cd backend && source venv/bin/activate && python -m app.main

# Start frontend
cd frontend && npm start
```

---

## Final Checklist

- [ ] Can start backend successfully
- [ ] Model is trained (ensemble_model.pkl exists)
- [ ] Can start frontend successfully
- [ ] Understand system architecture
- [ ] Can explain ML model approach (XGBoost + Holt-Winters)
- [ ] Know key metrics (R² 0.82, 17 features, model v2.0.0)
- [ ] Practiced demo flow
- [ ] Read all documentation
- [ ] Prepared for Q&A
