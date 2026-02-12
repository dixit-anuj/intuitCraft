# Quick Start Guide

Get your QuickBooks Commerce Sales Forecasting demo running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher

## Step 1: Setup & Train Backend

```bash
cd /Users/anujdixit/Desktop/IntuitCraft/backend

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Train the ML model (XGBoost + Holt-Winters ensemble)
python -m scripts.train_model

# Start the backend server
python -m app.main
```

The backend will start at: **http://localhost:8000**
API Documentation: **http://localhost:8000/docs**

## Step 2: Setup Frontend

Open a new terminal:

```bash
cd /Users/anujdixit/Desktop/IntuitCraft/frontend

# Install dependencies
npm install

# Start the React development server
npm start
```

The frontend will automatically open at: **http://localhost:3000**

## Step 3: Explore the Demo

### Backend API
Visit **http://localhost:8000/docs** to see:
- Interactive API documentation
- Try out endpoints
- View request/response schemas

### Frontend Dashboard
Visit **http://localhost:3000** to see:
- Sales forecasting dashboard with Intuit-themed design
- Category-wise predictions from the trained model
- Interactive charts with historical data and forecasts
- Top products by category with confidence intervals

## Quick Test Commands

### Test Backend Health
```bash
curl http://localhost:8000/api/v1/health
```

### Test Forecast API
```bash
curl "http://localhost:8000/api/v1/forecast/top-products?time_period=month&limit=5"
```

### Test Category Trend
```bash
curl "http://localhost:8000/api/v1/forecast/trends/Electronics?days=60"
```

## Explore the Code

### Backend Structure
```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── services/         # Business logic (uses trained model)
│   ├── models/           # ML models (XGBoost + Holt-Winters) & Pydantic schemas
│   └── core/             # Configuration
├── data/models/          # Trained model artifacts (ensemble_model.pkl)
├── notebooks/            # Jupyter notebooks
└── scripts/              # train_model.py
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/       # React components (Dashboard, Chart, etc.)
│   ├── services/         # API client (api.ts)
│   └── App.tsx           # Main application with skip-link, ARIA
```

## Features to Demonstrate

1. **Time Period Selection**: Toggle between week, month, and year forecasts
2. **Category Overview**: View predictions for all 8 product categories
3. **Detailed View**: Click a category to see historical trends and model forecasts
4. **Top Products**: See ranked products with predicted sales and revenue
5. **Confidence Intervals**: View prediction uncertainty ranges (95%)
6. **Accessibility**: Keyboard navigation, screen-reader support, focus indicators

## Training the Model

The model must be trained before the API serves real predictions:

```bash
cd backend
source venv/bin/activate
python -m scripts.train_model
```

This will:
- Generate 2 years of synthetic training data (8 categories, 5,848 records, 730 days)
- Train XGBoost (25 features, R² 0.999 on training data, Val R² 0.978)
- Train Holt-Winters per category (weekly seasonality)
- Evaluate on 30-day holdout (R² 0.96, MAE 4.1%, MAPE 4.3%)
- Save the ensemble model to `data/models/ensemble_model.pkl`

## Troubleshooting

### Backend won't start
```bash
python --version  # Should be 3.9+
pip install --upgrade -r requirements.txt
```

### "Model not loaded" error
```bash
# You need to train first
python -m scripts.train_model
```

### Frontend won't start
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port conflicts
```bash
# Find and kill process on port 8000
lsof -i :8000 -t | xargs kill

# Or use a different frontend port
PORT=3001 npm start
```

## Next Steps

1. Review the **System Design** document: `docs/SYSTEM_DESIGN.md`
2. Read the **ML Model Details**: `docs/ML_MODEL_DETAILS.md`
3. Check the **Model Comparison**: `docs/MODEL_COMPARISON.md`
4. Review the **Presentation**: `presentation/INTERVIEW_PRESENTATION.md`

## Key Talking Points

### Technical Excellence
- Ensemble ML model (XGBoost + Holt-Winters)
- 96% R² accuracy on 30-day holdout
- Real trained model — not mock data
- Accessible, Intuit-branded UI

### Business Value
- Helps merchants optimize inventory
- Predicts top-selling products per category
- Reduces overstock/understock
- Data-driven decision making

### Production Readiness
- RESTful API with Swagger documentation
- Error handling and structured logging
- Model training pipeline with evaluation
- WCAG-accessible frontend
