"""
Train the ensemble forecasting model
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
    
    logger.info("Starting model training...")
    
    # Load data
    data_service = DataService()
    df = data_service.load_sales_data()
    df = data_service.preprocess_data(df)
    
    logger.info(f"Loaded {len(df)} records")
    logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
    logger.info(f"Categories: {df['category'].unique()}")
    
    # Prepare for training
    # Add required columns
    df['product'] = df['category'] + '_product'
    if 'revenue' not in df.columns:
        df['revenue'] = df['sales'] * 50  # Mock price
    
    # Train model
    model = EnsembleForecastModel()
    
    logger.info("Training ensemble model...")
    model.train(df)
    
    # Save model
    model_path = "data/models"
    os.makedirs(model_path, exist_ok=True)
    model.save(model_path)
    
    logger.info(f"Model training complete and saved to {model_path}")
    
    # Test prediction
    logger.info("Testing predictions...")
    categories = df['category'].unique()[:3]
    predictions = model.predict(
        categories=list(categories),
        time_period='month'
    )
    
    for category, pred_df in predictions.items():
        logger.info(f"\n{category} - Next 7 days forecast:")
        logger.info(pred_df.head(7))
    
    logger.info("\nModel training and testing completed successfully!")


if __name__ == "__main__":
    main()
