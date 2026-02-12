"""
Data service - handles data loading, preprocessing, and external data sources
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List
from loguru import logger


class DataService:
    """Service for data management and preprocessing"""
    
    def __init__(self):
        self.data_cache = {}
    
    def load_sales_data(self, start_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Load sales data from storage
        
        In production, this would load from:
        - Database
        - Kaggle dataset
        - Data warehouse
        """
        # For demo, generate synthetic data
        return self._generate_synthetic_sales_data()
    
    def _generate_synthetic_sales_data(self, days: int = 730) -> pd.DataFrame:
        """
        Generate synthetic sales data for demo.
        
        2 years of daily data across 8 categories.
        Uses deterministic patterns with controlled noise so the model
        can learn real structure.
        """
        
        np.random.seed(42)  # Fixed seed for reproducible training data
        
        categories = [
            "Electronics", "Clothing & Apparel", "Home & Garden",
            "Sports & Outdoors", "Books & Media", "Food & Beverages",
            "Health & Beauty", "Toys & Games"
        ]
        
        # Category-specific base sales
        category_base = {
            "Electronics": 1800,
            "Clothing & Apparel": 1400,
            "Home & Garden": 1100,
            "Sports & Outdoors": 900,
            "Books & Media": 600,
            "Food & Beverages": 1200,
            "Health & Beauty": 1000,
            "Toys & Games": 750,
        }
        
        # Category-specific seasonality amplitude (some categories are more seasonal)
        category_seasonality = {
            "Electronics": 350,
            "Clothing & Apparel": 250,
            "Home & Garden": 200,
            "Sports & Outdoors": 300,
            "Books & Media": 150,
            "Food & Beverages": 100,
            "Health & Beauty": 120,
            "Toys & Games": 400,  # Very seasonal (holiday toys)
        }
        
        # Category-specific weekend boost
        category_weekend = {
            "Electronics": 250,
            "Clothing & Apparel": 200,
            "Home & Garden": 180,
            "Sports & Outdoors": 220,
            "Books & Media": 80,
            "Food & Beverages": 150,
            "Health & Beauty": 100,
            "Toys & Games": 160,
        }
        
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days)
        
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            for category in categories:
                base = category_base[category]
                
                # Slow upward trend (0.3 units/day)
                days_elapsed = (current_date - start_date).days
                trend = days_elapsed * 0.3
                
                # Annual seasonality (category-specific amplitude)
                day_of_year = current_date.timetuple().tm_yday
                amplitude = category_seasonality[category]
                seasonality = amplitude * np.sin(2 * np.pi * day_of_year / 365.25)
                
                # Monthly mini-cycle (beginning/end of month effects)
                day_of_month = current_date.day
                monthly_effect = 50 * np.sin(2 * np.pi * day_of_month / 30.5)
                
                # Weekend boost (category-specific)
                if current_date.weekday() >= 5:
                    weekend_boost = category_weekend[category]
                else:
                    weekend_boost = 0
                
                # Friday slight boost
                if current_date.weekday() == 4:
                    weekend_boost = category_weekend[category] * 0.3
                
                # Controlled noise (5% of base instead of 10%)
                noise = np.random.normal(0, base * 0.05)
                
                sales = max(0, base + trend + seasonality + monthly_effect + weekend_boost + noise)
                revenue = sales * np.random.uniform(20, 100)
                
                data.append({
                    'date': current_date,
                    'category': category,
                    'sales': round(sales, 2),
                    'revenue': round(revenue, 2),
                    'transactions': int(sales / np.random.uniform(5, 15))
                })
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(data)
    
    def get_external_indicators(self) -> dict:
        """
        Fetch external economic indicators
        
        In production, this would fetch from:
        - FRED API (Federal Reserve Economic Data)
        - Yahoo Finance
        - Other economic APIs
        """
        # Mock data for demo
        return {
            'gdp_growth': 2.8,
            'inflation_rate': 3.2,
            'consumer_confidence': 102.5,
            'unemployment_rate': 3.9,
            'retail_sales_growth': 4.5,
            'timestamp': datetime.now().isoformat()
        }
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess sales data for model training
        """
        df = df.copy()
        
        # Handle missing values
        df = df.fillna(0)
        
        # Remove outliers (optional)
        for col in ['sales', 'revenue']:
            if col in df.columns:
                q1 = df[col].quantile(0.01)
                q99 = df[col].quantile(0.99)
                df[col] = df[col].clip(lower=q1, upper=q99)
        
        # Ensure date is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def aggregate_by_period(
        self,
        df: pd.DataFrame,
        period: str = 'D'
    ) -> pd.DataFrame:
        """
        Aggregate sales data by time period
        
        Args:
            df: Sales data
            period: 'D' (day), 'W' (week), 'M' (month), 'Y' (year)
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        agg_df = df.groupby([pd.Grouper(key='date', freq=period), 'category']).agg({
            'sales': 'sum',
            'revenue': 'sum',
            'transactions': 'sum'
        }).reset_index()
        
        return agg_df
