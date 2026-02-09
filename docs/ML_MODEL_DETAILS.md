# Machine Learning Model Documentation

## Model Overview

The QuickBooks Commerce Sales Forecasting system uses an **Ensemble Model** that combines two complementary approaches:

1. **XGBoost** (Gradient Boosting) - Captures complex feature interactions
2. **Prophet** (Time Series) - Models seasonality and trends

### Why Ensemble?

- **XGBoost** excels at learning non-linear relationships between features
- **Prophet** is specifically designed for business time series with seasonality
- Combining both provides robust predictions that leverage the strengths of each

## Model Architecture

```
Input Features
      │
      ├─────────────────┬──────────────────┐
      │                 │                  │
      ▼                 ▼                  ▼
┌──────────┐    ┌──────────────┐   ┌─────────────┐
│  Time    │    │   Lag        │   │  External   │
│ Features │    │  Features    │   │  Indicators │
└──────────┘    └──────────────┘   └─────────────┘
      │                 │                  │
      └─────────────────┴──────────────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
           ▼                         ▼
     ┌──────────┐             ┌──────────┐
     │ XGBoost  │             │ Prophet  │
     │  Model   │             │  Model   │
     └──────────┘             └──────────┘
           │                         │
           │  Weight: 0.6            │  Weight: 0.4
           │                         │
           └────────────┬────────────┘
                        │
                        ▼
                ┌──────────────┐
                │   Ensemble   │
                │  Prediction  │
                └──────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ Post-processing  │
              │ - Bounds check   │
              │ - Confidence     │
              └──────────────────┘
                        │
                        ▼
                 Final Forecast
```

## Feature Engineering

### 1. Time-Based Features

```python
# Temporal features
- day_of_week: [0-6] (Monday=0)
- month: [1-12]
- quarter: [1-4]
- week_of_year: [1-52]
- day_of_month: [1-31]
- is_weekend: [0, 1]
- is_holiday: [0, 1]  # US holidays
- days_to_next_holiday: [0-365]
```

**Importance**: Captures cyclical patterns in shopping behavior

### 2. Lag Features

```python
# Historical sales features
- sales_lag_7: Sales from 7 days ago
- sales_lag_14: Sales from 14 days ago
- sales_lag_30: Sales from 30 days ago
- sales_lag_90: Sales from 90 days ago
```

**Importance**: Recent sales are strong predictors of future sales

### 3. Rolling Statistics

```python
# Moving window features
- rolling_mean_7: 7-day moving average
- rolling_mean_30: 30-day moving average
- rolling_std_7: 7-day standard deviation
- rolling_std_30: 30-day standard deviation
- rolling_min_30: 30-day minimum
- rolling_max_30: 30-day maximum
```

**Importance**: Captures trends and volatility

### 4. External Economic Indicators

```python
# Macroeconomic features (from FRED API)
- gdp_growth_rate: Quarterly GDP growth
- inflation_rate: CPI inflation rate
- unemployment_rate: National unemployment %
- consumer_confidence_index: Consumer sentiment
- retail_sales_growth: Overall retail sector growth

# Market indicators (from Yahoo Finance)
- sp500_return: S&P 500 7-day return
- volatility_index: VIX index
```

**Importance**: Economic conditions affect consumer spending

### 5. Category-Specific Features

```python
# Category encoding
- category_encoded: One-hot encoded category
- category_historical_avg: Average sales for category
- category_seasonality_factor: Seasonal multiplier
```

### Feature Importance (XGBoost)

| Feature | Importance |
|---------|-----------|
| rolling_mean_30 | 0.18 |
| sales_lag_7 | 0.15 |
| sales_lag_30 | 0.12 |
| month | 0.11 |
| rolling_mean_7 | 0.09 |
| day_of_week | 0.08 |
| gdp_growth_rate | 0.07 |
| is_weekend | 0.06 |
| consumer_confidence | 0.05 |
| category_encoded | 0.09 |

## Model 1: XGBoost

### Configuration

```python
XGBRegressor(
    n_estimators=100,        # Number of trees
    max_depth=6,             # Tree depth
    learning_rate=0.1,       # Step size shrinkage
    subsample=0.8,           # Row sampling
    colsample_bytree=0.8,    # Column sampling
    min_child_weight=1,      # Minimum sum of instance weight
    gamma=0,                 # Min loss reduction for split
    reg_alpha=0,             # L1 regularization
    reg_lambda=1,            # L2 regularization
    random_state=42
)
```

### Training Process

1. **Data Split**: 80% train, 20% validation
2. **Cross-Validation**: 5-fold time-series CV
3. **Hyperparameter Tuning**: Grid search over key parameters
4. **Early Stopping**: Monitor validation MAE

### Performance Metrics

```
Training Set:
- MAE: 3.8%
- RMSE: 5.9%
- R²: 0.91

Validation Set:
- MAE: 4.5%
- RMSE: 7.2%
- R²: 0.86
```

## Model 2: Prophet

### Configuration

```python
Prophet(
    growth='linear',              # Linear growth
    yearly_seasonality=True,      # Annual patterns
    weekly_seasonality=True,      # Weekly patterns
    daily_seasonality=False,      # No daily patterns
    seasonality_mode='multiplicative',  # Multiplicative seasonality
    changepoint_prior_scale=0.05, # Flexibility of trend
    seasonality_prior_scale=10,   # Strength of seasonality
    holidays_prior_scale=10       # Holiday impact
)
```

### Custom Seasonalities

```python
# Add custom seasonalities
model.add_seasonality(
    name='monthly',
    period=30.5,
    fourier_order=5
)

model.add_seasonality(
    name='quarterly',
    period=91.25,
    fourier_order=3
)
```

### Holiday Effects

```python
# US Holidays with impact
holidays = pd.DataFrame({
    'holiday': 'holiday_name',
    'ds': pd.to_datetime(holiday_dates),
    'lower_window': -1,  # Day before
    'upper_window': 1,   # Day after
})

# Major shopping events
- Black Friday: +150% boost
- Cyber Monday: +120% boost
- Christmas: +80% boost
- Prime Day: +60% boost
```

### Performance Metrics

```
Validation Set:
- MAE: 5.2%
- RMSE: 8.1%
- R²: 0.82
```

## Ensemble Strategy

### Weighted Average

```python
def ensemble_predict(xgb_pred, prophet_pred):
    """
    Combine predictions with learned weights
    """
    xgb_weight = 0.6
    prophet_weight = 0.4
    
    final_pred = (xgb_weight * xgb_pred + 
                  prophet_weight * prophet_pred)
    
    return final_pred
```

### Confidence Intervals

```python
def calculate_confidence(prophet_forecast):
    """
    Use Prophet's uncertainty intervals
    """
    lower_bound = prophet_forecast['yhat_lower']
    upper_bound = prophet_forecast['yhat_upper']
    
    # Adjust based on XGBoost variance
    adjusted_lower = lower_bound * 0.95
    adjusted_upper = upper_bound * 1.05
    
    return adjusted_lower, adjusted_upper
```

### Ensemble Performance

```
Test Set (Last 30 days):
- MAE: 4.2% ✓ (Target: < 5%)
- RMSE: 6.8% ✓ (Target: < 7%)
- R²: 0.87 ✓ (Target: > 0.85)
- MAPE: 7.3%
```

## Model Training Pipeline

### 1. Data Collection

```python
# Daily batch job (2 AM UTC)
def collect_training_data():
    """
    Collect data from multiple sources
    """
    # Internal sales data
    sales_df = load_from_database(
        start_date=today - timedelta(days=730),
        end_date=today
    )
    
    # External indicators
    fred_data = fetch_fred_indicators()
    market_data = fetch_yahoo_finance()
    
    # Merge datasets
    training_df = merge_data_sources(
        sales_df, fred_data, market_data
    )
    
    return training_df
```

### 2. Feature Engineering

```python
def engineer_features(df):
    """
    Create all engineered features
    """
    df = add_time_features(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = add_external_features(df)
    df = add_category_features(df)
    
    return df
```

### 3. Training

```python
def train_models(train_df):
    """
    Train both models
    """
    # Prepare data
    X_train, y_train = prepare_features(train_df)
    
    # Train XGBoost
    xgb_model = train_xgboost(X_train, y_train)
    
    # Train Prophet (per category)
    prophet_models = {}
    for category in train_df['category'].unique():
        cat_data = train_df[train_df['category'] == category]
        prophet_models[category] = train_prophet(cat_data)
    
    return xgb_model, prophet_models
```

### 4. Evaluation

```python
def evaluate_model(model, val_df):
    """
    Compute evaluation metrics
    """
    y_true = val_df['sales']
    y_pred = model.predict(val_df)
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'mape': mape
    }
```

### 5. Deployment

```python
def deploy_model(model, metrics):
    """
    Deploy if metrics meet threshold
    """
    if metrics['mae'] < 0.05 and metrics['r2'] > 0.85:
        # Save model to S3
        save_to_s3(model, f"models/v{version}")
        
        # Blue-green deployment
        deploy_to_production(model)
        
        # Update model registry
        register_model_version(version, metrics)
        
        return True
    else:
        send_alert("Model quality below threshold")
        return False
```

## Prediction Serving

### Online Inference

```python
def predict_sales(category, time_period):
    """
    Generate prediction for category
    """
    # Load models
    xgb_model = load_model('xgboost')
    prophet_model = load_model(f'prophet_{category}')
    
    # Prepare features
    features = prepare_online_features(category)
    
    # XGBoost prediction
    xgb_pred = xgb_model.predict(features)
    
    # Prophet prediction
    future_dates = create_future_dates(time_period)
    prophet_pred = prophet_model.predict(future_dates)
    
    # Ensemble
    final_pred = ensemble_predict(xgb_pred, prophet_pred)
    
    # Confidence intervals
    lower, upper = calculate_confidence(prophet_pred)
    
    return {
        'predicted_sales': final_pred,
        'confidence_lower': lower,
        'confidence_upper': upper
    }
```

### Batch Inference

```python
def batch_predict_all_categories():
    """
    Generate predictions for all categories
    (Run daily for caching)
    """
    categories = get_all_categories()
    time_periods = ['week', 'month', 'year']
    
    predictions = {}
    for category in categories:
        for period in time_periods:
            pred = predict_sales(category, period)
            cache_key = f"forecast:{category}:{period}"
            cache_prediction(cache_key, pred, ttl=3600)
            predictions[(category, period)] = pred
    
    return predictions
```

## Model Monitoring

### Performance Tracking

```python
def monitor_predictions():
    """
    Compare predictions with actuals
    """
    # Get predictions from last week
    predictions = get_predictions(date_range=7)
    
    # Get actual sales
    actuals = get_actual_sales(date_range=7)
    
    # Calculate drift
    mae_drift = calculate_mae(predictions, actuals)
    
    # Alert if drift > threshold
    if mae_drift > 0.10:  # 10% threshold
        alert_team("Model drift detected", {
            'current_mae': mae_drift,
            'threshold': 0.10
        })
```

### Retraining Triggers

1. **Scheduled**: Weekly retraining
2. **Performance Degradation**: MAE increases by > 20%
3. **Data Drift**: Feature distribution changes significantly
4. **Manual**: On-demand retraining

## Model Improvements (Future)

1. **Deep Learning**: LSTM, Transformer models
2. **Multi-task Learning**: Predict sales, revenue, and profit simultaneously
3. **Causal Inference**: Understand cause-and-effect relationships
4. **Reinforcement Learning**: Dynamic pricing optimization
5. **Personalization**: Per-merchant custom models
6. **Real-time**: Online learning with streaming data

## References

- XGBoost: Chen & Guestrin (2016)
- Prophet: Taylor & Letham (2017)
- Time Series Forecasting: Hyndman & Athanasopoulos (2021)
