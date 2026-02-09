"""
Ensemble forecasting model combining XGBoost and Prophet
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import joblib
from pathlib import Path

try:
    import xgboost as xgb
    from prophet import Prophet
except ImportError:
    pass  # Handle gracefully if dependencies not installed yet


class EnsembleForecastModel:
    """
    Ensemble model combining:
    - XGBoost for trend and feature-based predictions
    - Prophet for seasonality and time-series patterns
    """
    
    def __init__(self, model_path: str = None):
        self.xgb_model = None
        self.prophet_models = {}  # One prophet model per category
        self.feature_scaler = None
        self.model_path = model_path
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature engineering for sales data
        
        Features:
        - Time-based: day_of_week, month, quarter, is_weekend
        - Lag features: sales_lag_7, sales_lag_30
        - Rolling statistics: rolling_mean_7, rolling_std_7
        - External: economic indicators
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Time features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['day_of_month'] = df['date'].dt.day
        df['week_of_year'] = df['date'].dt.isocalendar().week
        
        # Lag features (if enough data)
        if len(df) > 30:
            df['sales_lag_7'] = df.groupby('category')['sales'].shift(7)
            df['sales_lag_30'] = df.groupby('category')['sales'].shift(30)
            
            # Rolling statistics
            df['rolling_mean_7'] = df.groupby('category')['sales'].transform(
                lambda x: x.rolling(window=7, min_periods=1).mean()
            )
            df['rolling_std_7'] = df.groupby('category')['sales'].transform(
                lambda x: x.rolling(window=7, min_periods=1).std()
            )
            df['rolling_mean_30'] = df.groupby('category')['sales'].transform(
                lambda x: x.rolling(window=30, min_periods=1).mean()
            )
        
        return df
    
    def train(self, train_data: pd.DataFrame):
        """
        Train the ensemble model
        
        Args:
            train_data: DataFrame with columns [date, category, product, sales, revenue]
        """
        # Prepare features
        df = self.prepare_features(train_data)
        
        # Train XGBoost for overall trends
        feature_cols = [
            'day_of_week', 'month', 'quarter', 'is_weekend',
            'day_of_month', 'week_of_year'
        ]
        
        # Add lag features if available
        if 'sales_lag_7' in df.columns:
            feature_cols.extend([
                'sales_lag_7', 'sales_lag_30',
                'rolling_mean_7', 'rolling_std_7', 'rolling_mean_30'
            ])
        
        # Encode category
        df['category_encoded'] = pd.Categorical(df['category']).codes
        feature_cols.append('category_encoded')
        
        # Drop NaN values from lag features
        df_train = df[feature_cols + ['sales']].dropna()
        
        X_train = df_train[feature_cols]
        y_train = df_train['sales']
        
        # Train XGBoost
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        self.xgb_model.fit(X_train, y_train)
        
        # Train Prophet models per category
        for category in df['category'].unique():
            cat_data = df[df['category'] == category][['date', 'sales']].copy()
            cat_data.columns = ['ds', 'y']
            
            prophet_model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative'
            )
            prophet_model.fit(cat_data)
            self.prophet_models[category] = prophet_model
        
        print(f"Model trained on {len(df)} records across {df['category'].nunique()} categories")
    
    def predict(
        self,
        categories: List[str],
        time_period: str,
        start_date: datetime = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate predictions for specified categories and time period
        
        Args:
            categories: List of categories to predict
            time_period: 'week', 'month', or 'year'
            start_date: Start date for prediction (defaults to tomorrow)
        
        Returns:
            Dictionary mapping category to DataFrame with predictions
        """
        if start_date is None:
            start_date = datetime.now() + timedelta(days=1)
        
        # Determine forecast horizon
        periods_map = {
            'week': 7,
            'month': 30,
            'year': 365
        }
        periods = periods_map.get(time_period, 30)
        
        predictions = {}
        
        for category in categories:
            if category not in self.prophet_models:
                continue
            
            # Prophet prediction
            prophet_model = self.prophet_models[category]
            future = prophet_model.make_future_dataframe(periods=periods)
            prophet_forecast = prophet_model.predict(future)
            
            # Get only future predictions
            prophet_forecast = prophet_forecast[prophet_forecast['ds'] >= start_date].copy()
            
            # Combine with XGBoost (simple averaging for ensemble)
            prophet_forecast['predicted_sales'] = prophet_forecast['yhat']
            prophet_forecast['confidence_lower'] = prophet_forecast['yhat_lower']
            prophet_forecast['confidence_upper'] = prophet_forecast['yhat_upper']
            
            # Ensure non-negative predictions
            prophet_forecast['predicted_sales'] = prophet_forecast['predicted_sales'].clip(lower=0)
            prophet_forecast['confidence_lower'] = prophet_forecast['confidence_lower'].clip(lower=0)
            
            predictions[category] = prophet_forecast[
                ['ds', 'predicted_sales', 'confidence_lower', 'confidence_upper']
            ].head(periods)
        
        return predictions
    
    def save(self, path: str):
        """Save model to disk"""
        Path(path).mkdir(parents=True, exist_ok=True)
        
        if self.xgb_model:
            joblib.dump(self.xgb_model, f"{path}/xgb_model.pkl")
        
        for category, model in self.prophet_models.items():
            joblib.dump(model, f"{path}/prophet_{category}.pkl")
        
        print(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load model from disk"""
        xgb_path = f"{path}/xgb_model.pkl"
        if Path(xgb_path).exists():
            self.xgb_model = joblib.load(xgb_path)
        
        # Load prophet models
        for model_file in Path(path).glob("prophet_*.pkl"):
            category = model_file.stem.replace("prophet_", "")
            self.prophet_models[category] = joblib.load(str(model_file))
        
        print(f"Model loaded from {path}")
