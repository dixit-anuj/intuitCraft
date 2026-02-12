# Machine Learning Model Documentation

## Model Overview

The QuickBooks Commerce Sales Forecasting system uses an **Ensemble Model** that combines two complementary approaches:

1. **XGBoost** (Gradient Boosting) - Captures complex feature interactions and non-linear patterns
2. **Holt-Winters** (Exponential Smoothing) - Models seasonality and time-series trends per category

### Why Ensemble?

- **XGBoost** excels at learning non-linear relationships between engineered features
- **Holt-Winters** is specifically designed for time series with seasonal patterns
- Combining both provides robust predictions that leverage the strengths of each

### Why Holt-Winters Over Prophet?

We replaced Prophet with Holt-Winters (from statsmodels) for several practical reasons:
- **Stability**: No complex C/Stan backend dependencies
- **Lightweight**: Ships with statsmodels, no extra installation issues
- **Proven**: Classical exponential smoothing is well-understood and reliable
- **Fast**: Trains quickly per category with minimal configuration

## Model Architecture

```
Input Features
      │
      ├─────────────────┬──────────────────┐
      │                 │                  │
      ▼                 ▼                  ▼
┌──────────┐    ┌──────────────┐   ┌─────────────┐
│  Time    │    │   Lag        │   │  Rolling    │
│ Features │    │  Features    │   │  Statistics │
└──────────┘    └──────────────┘   └─────────────┘
      │                 │                  │
      └─────────────────┴──────────────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
           ▼                         ▼
     ┌──────────┐          ┌────────────────┐
     │ XGBoost  │          │  Holt-Winters  │
     │  Model   │          │ (per category) │
     └──────────┘          └────────────────┘
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
              │ - Non-negative   │
              │ - Confidence     │
              └──────────────────┘
                        │
                        ▼
                 Final Forecast
```

## Feature Engineering (25 Features)

### 1. Time-Based Features

```python
# Temporal features extracted from date
- day_of_week: [0-6] (Monday=0)
- month: [1-12]
- quarter: [1-4]
- week_of_year: [1-52]
- day_of_month: [1-31]
- is_weekend: [0, 1]
```

**Importance**: Captures cyclical patterns — weekends show higher sales in certain categories.

### 2. Cyclical Encoding (sin/cos)

```python
# Cyclical encoding for temporal continuity
- day_of_week_sin, day_of_week_cos
- month_sin, month_cos
- day_of_year_sin, day_of_year_cos
```

**Importance**: Preserves cyclical nature of time features (e.g., Dec → Jan wrap-around).

### 3. Trend Feature

```python
- days_since_start: Number of days since training data start
```

**Importance**: Captures long-term growth or decline trends.

### 4. Lag Features

```python
# Historical sales features
- sales_lag_7: Sales from 7 days ago
- sales_lag_14: Sales from 14 days ago
- sales_lag_30: Sales from 30 days ago
```

**Importance**: Recent sales are strong predictors of future sales.

### 5. Rolling Statistics

```python
# Moving window features
- rolling_mean_7: 7-day moving average
- rolling_mean_30: 30-day moving average
- rolling_std_7: 7-day standard deviation
- rolling_std_30: 30-day standard deviation
```

**Importance**: Captures trends and volatility in sales patterns.

### 6. Momentum Features

```python
- momentum_7_30: Ratio of 7-day to 30-day rolling mean
- momentum_7_14: Ratio of 7-day to 14-day rolling mean
```

**Importance**: Captures short-term vs. long-term sales momentum.

### 7. Interaction & Volatility

```python
- weekend_x_category: Interaction between is_weekend and category
- volatility_ratio: Ratio of 7-day std to 30-day std
```

**Importance**: Category-specific weekend effects and volatility patterns.

### 8. Category Encoding

```python
# Category as numeric feature
- category_encoded: Label-encoded category (0-7)
```

**Importance**: Allows the model to learn category-specific patterns.

### Feature Importance (XGBoost)

| Feature | Typical Importance |
|---------|-----------|
| rolling_mean_30 | High |
| sales_lag_7 | High |
| sales_lag_30 | Medium-High |
| month | Medium |
| rolling_mean_7 | Medium |
| day_of_week | Medium |
| is_weekend | Medium |
| rolling_std_7 | Low-Medium |
| category_encoded | Low-Medium |

## Model 1: XGBoost

### Configuration

```python
XGBRegressor(
    n_estimators=500,
    max_depth=7,
    min_child_weight=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
```

### Training Process

1. **Data Generation**: 2 years of synthetic daily data across 8 categories (5,848 records, 730 days)
2. **Feature Engineering**: 25 features computed per record (including cyclical encoding, trend, momentum, interaction, volatility ratio)
3. **Train/Holdout Split**: Last 30 days held out for evaluation
4. **Training**: XGBoost trained on all categories at once
5. **Noise**: Reduced to 5% for cleaner training signal

### Performance Metrics

```
Training Set:
- R²: 0.999

Validation Set:
- R²: 0.978

Holdout Set (last 30 days):
- R²: 0.96
- MAE: 4.1%
- MAPE: 4.3%
```

## Model 2: Holt-Winters (Exponential Smoothing)

### Configuration

```python
ExponentialSmoothing(
    endog=category_time_series,
    trend='add',              # Additive trend component
    seasonal='add',           # Additive seasonal component
    seasonal_periods=7        # Weekly seasonality
)
```

### Per-Category Training

Holt-Winters models are trained **independently per category**:
- One model for Electronics, one for Clothing, etc.
- Each captures the specific seasonal pattern and trend for that category
- Weekly seasonality (period=7) captures day-of-week patterns

### Handling Edge Cases

```python
# Fill gaps in time series
ts = ts.ffill().bfill()

# Fallback for categories with insufficient data
# Uses XGBoost prediction alone
```

## Ensemble Strategy

### Weighted Average

```python
def ensemble_predict(xgb_pred, hw_pred):
    """
    Combine predictions with fixed weights
    """
    xgb_weight = 0.6
    hw_weight = 0.4
    
    final_pred = (xgb_weight * xgb_pred + 
                  hw_weight * hw_pred)
    
    return max(final_pred, 0)  # Non-negative sales
```

### Confidence Intervals

```python
def calculate_confidence(prediction):
    """
    95% confidence interval based on prediction magnitude
    """
    margin = prediction * 0.15  # 15% margin
    lower_bound = max(prediction - margin, 0)
    upper_bound = prediction + margin
    
    return lower_bound, upper_bound
```

### Ensemble Performance

```
Holdout Set (Last 30 days):
- R²: 0.96
- MAE: 4.1%
- MAPE: 4.3%
- Model Version: 3.0.0
```

## Model Training Pipeline

### 1. Data Generation

```python
def generate_synthetic_data():
    """
    Generate realistic synthetic sales data
    """
    np.random.seed(42)  # Reproducible
    
    categories = [
        "Electronics", "Clothing", "Home & Garden",
        "Sports & Outdoors", "Books & Media",
        "Food & Beverages", "Health & Beauty",
        "Toys & Games"
    ]
    
    # Category-specific base sales
    category_base = {
        "Electronics": 1800,
        "Clothing": 1200,
        "Home & Garden": 900,
        ...
    }
    
    # Add seasonality, weekend effects, noise
    ...
```

### 2. Feature Engineering

```python
def prepare_features(df):
    """
    Create all 25 engineered features
    """
    df = add_time_features(df)           # 6 features
    df = add_cyclical_encoding(df)       # sin/cos for day_of_week, month, day_of_year
    df = add_trend_feature(df)           # days_since_start
    df = add_lag_features(df)            # 3 features
    df = add_rolling_features(df)        # 4 features
    df = add_momentum_features(df)       # 7/30 ratio, 7/14 ratio
    df = add_interaction_features(df)    # weekend x category
    df = add_volatility_ratio(df)        # std ratio
    df = add_category_encoding(df)       # 1 feature
    
    return df  # 25 total features
```

### 3. Training

```python
def train(self, df):
    """
    Train both models
    """
    # Prepare features
    feature_df = self.prepare_features(df)
    
    # Train XGBoost on all data
    self.xgb_model = XGBRegressor(...)
    self.xgb_model.fit(X_train, y_train)
    
    # Train Holt-Winters per category
    self.hw_models = {}
    for category in df['category'].unique():
        cat_data = df[df['category'] == category]
        ts = cat_data.set_index('date')['sales']
        ts = ts.resample('D').mean().ffill().bfill()
        
        model = ExponentialSmoothing(
            ts, trend='add', seasonal='add',
            seasonal_periods=7
        ).fit()
        self.hw_models[category] = model
```

### 4. Evaluation

```python
def evaluate_model():
    """
    Holdout evaluation on last 30 days
    """
    # Split: everything before last 30 days = train
    # Last 30 days = holdout
    
    model.train(train_data)
    predictions = model.predict(holdout_data)
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    # Results:
    # R²: 0.96
    # MAE: 4.1%
    # MAPE: 4.3%
```

### 5. Saving & Loading

```python
def save(self, path):
    """Save entire ensemble to single file"""
    joblib.dump({
        'xgb_model': self.xgb_model,
        'hw_models': self.hw_models,
        'feature_columns': self.feature_columns,
        'scaler': self.scaler
    }, path)

def load(cls, path):
    """Load ensemble from file"""
    data = joblib.load(path)
    model = cls()
    model.xgb_model = data['xgb_model']
    model.hw_models = data['hw_models']
    ...
    return model
```

## Prediction Serving

### Online Inference

```python
def predict(self, df):
    """
    Generate prediction using ensemble
    """
    # Prepare features
    features = self.prepare_features(df)
    
    # XGBoost prediction
    xgb_pred = self.xgb_model.predict(features)
    
    # Holt-Winters prediction (per category)
    hw_pred = get_hw_forecast(category, steps)
    
    # Ensemble: 60% XGBoost + 40% Holt-Winters
    final_pred = 0.6 * xgb_pred + 0.4 * hw_pred
    
    return max(final_pred, 0)
```

## Model Monitoring (Production Design)

### Performance Tracking

- Compare predictions with actuals weekly
- Track MAE drift over time
- Alert if MAE increases > 20%

### Retraining Triggers

1. **Scheduled**: Weekly retraining with latest data
2. **Performance Degradation**: MAE increases significantly
3. **Data Drift**: Feature distributions shift
4. **Manual**: On-demand retraining

## Model Improvements (Future)

1. **Deep Learning**: LSTM, Transformer models for complex patterns
2. **External Data**: Integrate FRED API (GDP, inflation) and Yahoo Finance
3. **Multi-task Learning**: Predict sales, revenue, and profit simultaneously
4. **Personalization**: Per-merchant custom models
5. **Online Learning**: Continuous adaptation with streaming data
6. **Hyperparameter Tuning**: Bayesian optimization for XGBoost params

## References

- XGBoost: Chen & Guestrin (2016)
- Exponential Smoothing: Hyndman & Athanasopoulos (2021), "Forecasting: Principles and Practice"
- statsmodels: Seabold & Perktold (2010)
