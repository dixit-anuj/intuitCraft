# QuickBooks Commerce Sales Forecasting System

## Overview
A production-ready sales forecasting system that predicts top-selling products by category across different time periods for QuickBooks Commerce users.

## Features
- **Time-series Forecasting**: Predict sales for week, month, and year timeframes
- **Category-wise Analysis**: Top products by category with confidence intervals
- **Optimized ML Model**: Ensemble of XGBoost + Holt-Winters for accuracy
- **External Data Integration**: Architecture ready for economic indicators and market trends
- **Modern UI**: Interactive React dashboard with Intuit-themed design and WCAG accessibility
- **High Performance**: FastAPI backend with async endpoints

## Tech Stack
- **Backend**: Python 3.9, FastAPI, Scikit-learn, XGBoost, statsmodels
- **Frontend**: React 18, TypeScript, Recharts, Custom CSS (Intuit theme)
- **ML**: Ensemble modeling (XGBoost 60% + Holt-Winters 40%), 17 engineered features
- **Data**: Synthetic sales data with realistic seasonality, category-specific baselines

## Project Structure
```
IntuitCraft/
├── backend/              # FastAPI service
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # ML models & schemas
│   │   ├── services/    # Business logic
│   │   └── core/        # Configuration
│   ├── data/models/     # Trained model artifacts
│   ├── notebooks/       # Jupyter notebooks
│   ├── scripts/         # Training scripts
│   └── requirements.txt
├── frontend/            # React application
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── services/    # API clients
│   │   └── App.tsx      # Main app
│   └── package.json
├── presentation/        # Interview materials
└── docs/               # Documentation
```

## Quick Start

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Train the model
python -m scripts.train_model

# Start the server
python -m app.main
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Access
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Model Performance

Ensemble model (XGBoost + Holt-Winters) evaluated on 30-day holdout:

| Metric | Value |
|--------|-------|
| R² Score | 0.82 |
| MAE | 11% |
| XGBoost Train R² | 0.98 |

## System Architecture

1. **Data Layer**: Synthetic sales data with category-specific baselines, seasonality, and weekend patterns
2. **ML Layer**: Ensemble model — XGBoost for feature-based predictions, Holt-Winters for time-series seasonality
3. **API Layer**: FastAPI with RESTful endpoints and auto-generated Swagger docs
4. **Presentation Layer**: React dashboard with Intuit brand colors, WCAG accessibility, keyboard navigation

## Author
Built for Intuit Interview Demo
