"""
Ensemble forecasting model combining XGBoost and Exponential Smoothing (statsmodels)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import joblib
from pathlib import Path
from loguru import logger

import xgboost as xgb
from statsmodels.tsa.holtwinters import ExponentialSmoothing


class EnsembleForecastModel:
    """
    Ensemble model combining:
    - XGBoost for trend and feature-based predictions
    - Holt-Winters Exponential Smoothing for seasonality and time-series patterns
    
    The ensemble averages both models' predictions for robust forecasts.
    """
    
    def __init__(self, model_path: str = None):
        self.xgb_models: Dict[str, xgb.XGBRegressor] = {}  # One per category
        self.hw_models: Dict[str, dict] = {}  # Holt-Winters params per category
        self.category_encodings: Dict[str, int] = {}
        self.feature_cols: List[str] = []
        self.model_path = model_path
        self.is_trained = False
        self._training_data: Optional[pd.DataFrame] = None
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature engineering for sales data
        
        Features:
        - Time-based: day_of_week, month, quarter, is_weekend, day_of_month, week_of_year
        - Lag features: sales_lag_7, sales_lag_14, sales_lag_30
        - Rolling statistics: rolling_mean_7, rolling_std_7, rolling_mean_30
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['category', 'date'])
        
        # Time features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['day_of_month'] = df['date'].dt.day
        df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
        df['day_of_year'] = df['date'].dt.dayofyear
        
        # Lag features
        for lag in [7, 14, 30]:
            df[f'sales_lag_{lag}'] = df.groupby('category')['sales'].shift(lag)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'rolling_mean_{window}'] = df.groupby('category')['sales'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            df[f'rolling_std_{window}'] = df.groupby('category')['sales'].transform(
                lambda x: x.rolling(window=window, min_periods=1).std().fillna(0)
            )
        
        return df
    
    def train(self, train_data: pd.DataFrame):
        """
        Train the ensemble model
        
        Args:
            train_data: DataFrame with columns [date, category, sales, revenue]
        """
        df = self.prepare_features(train_data)
        self._training_data = train_data.copy()
        
        # Build category encodings
        categories = sorted(df['category'].unique())
        self.category_encodings = {cat: i for i, cat in enumerate(categories)}
        df['category_encoded'] = df['category'].map(self.category_encodings)
        
        # Define feature columns
        self.feature_cols = [
            'day_of_week', 'month', 'quarter', 'is_weekend',
            'day_of_month', 'week_of_year', 'day_of_year', 'category_encoded',
            'sales_lag_7', 'sales_lag_14', 'sales_lag_30',
            'rolling_mean_7', 'rolling_std_7',
            'rolling_mean_14', 'rolling_std_14',
            'rolling_mean_30', 'rolling_std_30',
        ]
        
        # Drop rows with NaN from lag features
        df_train = df.dropna(subset=self.feature_cols)
        
        X_train = df_train[self.feature_cols]
        y_train = df_train['sales']
        
        # === Train global XGBoost model ===
        logger.info(f"Training XGBoost on {len(X_train)} samples...")
        global_xgb = xgb.XGBRegressor(
            n_estimators=200,
            learning_rate=0.08,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            reg_alpha=0.1,
            reg_lambda=1.0,
        )
        global_xgb.fit(X_train, y_train)
        self.xgb_models['_global'] = global_xgb
        
        # Evaluate on training data
        train_preds = global_xgb.predict(X_train)
        train_mae = np.mean(np.abs(y_train - train_preds))
        train_r2 = 1 - np.sum((y_train - train_preds) ** 2) / np.sum((y_train - np.mean(y_train)) ** 2)
        logger.info(f"  XGBoost train MAE: {train_mae:.2f}, R²: {train_r2:.3f}")
        
        # === Train Holt-Winters per category ===
        logger.info("Training Holt-Winters per category...")
        for category in categories:
            cat_data = df[df['category'] == category].sort_values('date')
            ts = cat_data.set_index('date')['sales']
            
            # Resample to ensure daily frequency (fill gaps)
            ts = ts.asfreq('D')
            ts = ts.ffill().bfill()
            
            try:
                hw_model = ExponentialSmoothing(
                    ts,
                    trend='add',
                    seasonal='add',
                    seasonal_periods=7,  # Weekly seasonality
                ).fit(optimized=True)
                
                # Store the fitted values and params for later reconstruction
                self.hw_models[category] = {
                    'model': hw_model,
                    'last_date': ts.index[-1],
                    'last_values': ts.tail(30).values.tolist(),
                }
                logger.info(f"  {category}: Holt-Winters AIC={hw_model.aic:.1f}")
            except Exception as e:
                logger.warning(f"  {category}: Holt-Winters failed ({e}), using XGBoost only")
                self.hw_models[category] = None
        
        self.is_trained = True
        logger.info(f"Model trained on {len(df)} records across {len(categories)} categories")
    
    def predict(
        self,
        categories: List[str],
        time_period: str,
        start_date: datetime = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate predictions for specified categories and time period
        
        Returns:
            Dictionary mapping category to DataFrame with columns:
            [ds, predicted_sales, confidence_lower, confidence_upper]
        """
        if not self.is_trained:
            raise RuntimeError("Model has not been trained yet")
        
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        periods_map = {'week': 7, 'month': 30, 'year': 365}
        periods = periods_map.get(time_period, 30)
        
        predictions = {}
        
        for category in categories:
            if category not in self.category_encodings:
                logger.warning(f"Unknown category: {category}")
                continue
            
            forecast_dates = pd.date_range(start=start_date, periods=periods, freq='D')
            
            # --- Holt-Winters forecast ---
            hw_preds = None
            if category in self.hw_models and self.hw_models[category] is not None:
                try:
                    hw_model = self.hw_models[category]['model']
                    hw_forecast = hw_model.forecast(periods)
                    hw_preds = hw_forecast.values
                except Exception as e:
                    logger.warning(f"HW forecast failed for {category}: {e}")
            
            # --- XGBoost forecast (rolling) ---
            xgb_preds = self._xgb_rolling_forecast(category, start_date, periods)
            
            # --- Ensemble: weighted average ---
            if hw_preds is not None and len(hw_preds) == periods:
                # 60% XGBoost, 40% Holt-Winters
                ensemble_preds = 0.6 * xgb_preds + 0.4 * hw_preds
            else:
                ensemble_preds = xgb_preds
            
            # Ensure non-negative
            ensemble_preds = np.clip(ensemble_preds, 0, None)
            
            # Confidence intervals (based on training residual std)
            residual_std = self._get_residual_std(category)
            confidence_lower = np.clip(ensemble_preds - 1.96 * residual_std, 0, None)
            confidence_upper = ensemble_preds + 1.96 * residual_std
            
            predictions[category] = pd.DataFrame({
                'ds': forecast_dates,
                'predicted_sales': np.round(ensemble_preds, 2),
                'confidence_lower': np.round(confidence_lower, 2),
                'confidence_upper': np.round(confidence_upper, 2),
            })
        
        return predictions
    
    def get_historical_data(self, category: str, days: int = 90) -> pd.DataFrame:
        """Get historical training data for a category"""
        if self._training_data is None:
            return pd.DataFrame()
        
        df = self._training_data.copy()
        df['date'] = pd.to_datetime(df['date'])
        cat_data = df[df['category'] == category].sort_values('date')
        
        if days:
            cutoff = cat_data['date'].max() - timedelta(days=days)
            cat_data = cat_data[cat_data['date'] >= cutoff]
        
        return cat_data[['date', 'sales', 'revenue']].reset_index(drop=True)
    
    def _xgb_rolling_forecast(self, category: str, start_date: datetime, periods: int) -> np.ndarray:
        """Generate XGBoost predictions using rolling features"""
        global_model = self.xgb_models.get('_global')
        if global_model is None:
            return np.full(periods, 1000.0)
        
        # Get recent historical sales for lag features
        if self._training_data is not None:
            cat_hist = self._training_data[self._training_data['category'] == category].copy()
            cat_hist['date'] = pd.to_datetime(cat_hist['date'])
            cat_hist = cat_hist.sort_values('date')
            recent_sales = cat_hist['sales'].tail(60).tolist()
        else:
            recent_sales = [1000.0] * 60
        
        preds = []
        sales_buffer = list(recent_sales)
        
        for i in range(periods):
            current_date = start_date + timedelta(days=i)
            
            features = {
                'day_of_week': current_date.weekday(),
                'month': current_date.month,
                'quarter': (current_date.month - 1) // 3 + 1,
                'is_weekend': 1 if current_date.weekday() >= 5 else 0,
                'day_of_month': current_date.day,
                'week_of_year': current_date.isocalendar()[1],
                'day_of_year': current_date.timetuple().tm_yday,
                'category_encoded': self.category_encodings.get(category, 0),
                'sales_lag_7': sales_buffer[-7] if len(sales_buffer) >= 7 else sales_buffer[-1],
                'sales_lag_14': sales_buffer[-14] if len(sales_buffer) >= 14 else sales_buffer[-1],
                'sales_lag_30': sales_buffer[-30] if len(sales_buffer) >= 30 else sales_buffer[-1],
                'rolling_mean_7': np.mean(sales_buffer[-7:]),
                'rolling_std_7': np.std(sales_buffer[-7:]) if len(sales_buffer) >= 7 else 0,
                'rolling_mean_14': np.mean(sales_buffer[-14:]),
                'rolling_std_14': np.std(sales_buffer[-14:]) if len(sales_buffer) >= 14 else 0,
                'rolling_mean_30': np.mean(sales_buffer[-30:]),
                'rolling_std_30': np.std(sales_buffer[-30:]) if len(sales_buffer) >= 30 else 0,
            }
            
            X = pd.DataFrame([features])[self.feature_cols]
            pred = float(global_model.predict(X)[0])
            pred = max(0, pred)
            preds.append(pred)
            sales_buffer.append(pred)
        
        return np.array(preds)
    
    def _get_residual_std(self, category: str) -> float:
        """Get residual standard deviation for confidence intervals"""
        if self._training_data is None:
            return 100.0
        
        cat_data = self._training_data[self._training_data['category'] == category]
        if len(cat_data) == 0:
            return 100.0
        
        return float(cat_data['sales'].std() * 0.5)
    
    def save(self, path: str):
        """Save model to disk"""
        Path(path).mkdir(parents=True, exist_ok=True)
        
        save_data = {
            'xgb_models': self.xgb_models,
            'hw_models': {
                cat: {'model': info['model'], 'last_date': info['last_date'], 'last_values': info['last_values']}
                if info is not None else None
                for cat, info in self.hw_models.items()
            },
            'category_encodings': self.category_encodings,
            'feature_cols': self.feature_cols,
            'is_trained': self.is_trained,
            'training_data': self._training_data,
        }
        
        joblib.dump(save_data, f"{path}/ensemble_model.pkl")
        logger.info(f"Model saved to {path}/ensemble_model.pkl")
    
    def load(self, path: str):
        """Load model from disk"""
        model_file = Path(path) / "ensemble_model.pkl"
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")
        
        save_data = joblib.load(str(model_file))
        
        self.xgb_models = save_data['xgb_models']
        self.hw_models = save_data['hw_models']
        self.category_encodings = save_data['category_encodings']
        self.feature_cols = save_data['feature_cols']
        self.is_trained = save_data['is_trained']
        self._training_data = save_data.get('training_data')
        
        logger.info(f"Model loaded from {model_file} ({len(self.category_encodings)} categories)")
