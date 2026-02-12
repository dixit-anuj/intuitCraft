"""
Train the ensemble forecasting model (v3.0)

Improvements over v2.0:
- 2 years of training data (was 1 year)
- 25 features (was 17): cyclical encoding, momentum, trend, interactions
- Early stopping with validation set
- Reduced data noise (5% vs 10%)
- Per-category residual tracking for confidence intervals
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

from app.models.forecast_model import EnsembleForecastModel
from app.services.data_service import DataService


def main():
    """Train and save the forecasting model"""
    
    logger.info("=" * 60)
    logger.info("Starting model training (v3.0)...")
    logger.info("=" * 60)
    
    # Load data
    data_service = DataService()
    df = data_service.load_sales_data()
    df = data_service.preprocess_data(df)
    
    logger.info(f"Loaded {len(df)} records")
    logger.info(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    logger.info(f"Categories: {list(df['category'].unique())}")
    logger.info(f"Days of data: {(df['date'].max() - df['date'].min()).days}")
    
    # Train model on full data
    model = EnsembleForecastModel()
    
    logger.info("\nTraining ensemble model (XGBoost + Holt-Winters)...")
    model.train(df)
    
    # Save model
    model_path = "data/models"
    os.makedirs(model_path, exist_ok=True)
    model.save(model_path)
    
    logger.info(f"\nModel saved to {model_path}")
    
    # Test predictions
    logger.info("\n" + "=" * 60)
    logger.info("Testing predictions...")
    logger.info("=" * 60)
    
    categories = list(df['category'].unique())[:3]
    predictions = model.predict(
        categories=categories,
        time_period='week'
    )
    
    for category, pred_df in predictions.items():
        logger.info(f"\n{category} - Next 7 days forecast:")
        for _, row in pred_df.iterrows():
            logger.info(
                f"  {row['ds'].strftime('%Y-%m-%d')}: "
                f"{row['predicted_sales']:.0f} units "
                f"[{row['confidence_lower']:.0f} - {row['confidence_upper']:.0f}]"
            )
    
    # === Holdout Evaluation ===
    logger.info("\n" + "=" * 60)
    logger.info("Holdout evaluation (last 30 days withheld)...")
    logger.info("=" * 60)
    
    split_date = df['date'].max() - pd.Timedelta(days=30)
    train_df = df[df['date'] <= split_date]
    test_df = df[df['date'] > split_date]
    
    logger.info(f"Train: {len(train_df)} records, Test: {len(test_df)} records")
    
    eval_model = EnsembleForecastModel()
    eval_model.train(train_df)
    
    all_actual = []
    all_predicted = []
    
    for category in df['category'].unique():
        cat_test = test_df[test_df['category'] == category].sort_values('date')
        if len(cat_test) == 0:
            continue
        
        preds = eval_model.predict(
            categories=[category],
            time_period='month',
            start_date=cat_test['date'].min()
        )
        
        if category in preds:
            pred_df = preds[category]
            n = min(len(cat_test), len(pred_df))
            actual_vals = cat_test['sales'].values[:n]
            pred_vals = pred_df['predicted_sales'].values[:n]
            all_actual.extend(actual_vals)
            all_predicted.extend(pred_vals)
            
            # Per-category metrics
            cat_mae = np.mean(np.abs(actual_vals - pred_vals))
            cat_r2 = 1 - np.sum((actual_vals - pred_vals) ** 2) / np.sum((actual_vals - np.mean(actual_vals)) ** 2)
            logger.info(f"  {category}: MAE={cat_mae:.1f}, R²={cat_r2:.3f}")
    
    if all_actual:
        actual = np.array(all_actual)
        predicted = np.array(all_predicted)
        mae = np.mean(np.abs(actual - predicted))
        mae_pct = (mae / np.mean(actual)) * 100
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        r2 = 1 - np.sum((actual - predicted) ** 2) / np.sum((actual - np.mean(actual)) ** 2)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        
        logger.info(f"\n  Overall Holdout Metrics:")
        logger.info(f"  MAE:  {mae:.1f} ({mae_pct:.1f}% of mean sales)")
        logger.info(f"  RMSE: {rmse:.1f}")
        logger.info(f"  R²:   {r2:.3f}")
        logger.info(f"  MAPE: {mape:.1f}%")
    
    logger.info("\n" + "=" * 60)
    logger.info("Training complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
