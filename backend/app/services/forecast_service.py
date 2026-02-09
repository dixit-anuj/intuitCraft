"""
Forecasting service - orchestrates predictions and data aggregation
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from loguru import logger

from app.models.schemas import (
    ForecastRequest,
    ForecastResponse,
    TopProductsResponse,
    CategoryForecast,
    ProductForecast,
    CategoryTrendResponse,
    TrendDataPoint
)
from app.services.data_service import DataService


class ForecastService:
    """Service for generating sales forecasts"""
    
    def __init__(self):
        self.data_service = DataService()
        self._mock_mode = True  # Use mock data for demo
    
    async def generate_forecast(
        self,
        request: ForecastRequest
    ) -> ForecastResponse:
        """Generate comprehensive forecast based on request"""
        
        categories = request.categories or self._get_all_categories()
        predictions = []
        
        for category in categories:
            category_forecast = await self._forecast_category(
                category=category,
                time_period=request.time_period,
                include_confidence=request.include_confidence
            )
            predictions.append(category_forecast)
        
        return ForecastResponse(
            time_period=request.time_period,
            forecast_date=datetime.now(),
            predictions=predictions,
            model_version="1.0.0",
            accuracy_score=0.87
        )
    
    async def get_top_products(
        self,
        time_period: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> TopProductsResponse:
        """Get top-selling products for specified period"""
        
        # Validate time period
        if time_period not in ['week', 'month', 'year']:
            raise ValueError(f"Invalid time period: {time_period}")
        
        # Get predictions
        categories = [category] if category else self._get_all_categories()
        all_products = []
        
        for cat in categories:
            products = await self._get_top_products_for_category(
                category=cat,
                time_period=time_period,
                limit=limit if category else 5  # Fewer per category if showing all
            )
            all_products.extend(products)
        
        # Sort by predicted sales and limit
        all_products.sort(key=lambda x: x.predicted_sales, reverse=True)
        top_products = all_products[:limit]
        
        return TopProductsResponse(
            time_period=time_period,
            category=category,
            products=top_products,
            total_count=len(top_products),
            generated_at=datetime.now()
        )
    
    async def get_category_forecasts(
        self,
        time_period: str
    ) -> List[CategoryForecast]:
        """Get forecasts for all categories"""
        
        if time_period not in ['week', 'month', 'year']:
            raise ValueError(f"Invalid time period: {time_period}")
        
        categories = self._get_all_categories()
        forecasts = []
        
        for category in categories:
            forecast = await self._forecast_category(
                category=category,
                time_period=time_period,
                include_confidence=True
            )
            forecasts.append(forecast)
        
        return forecasts
    
    async def get_category_trend(
        self,
        category: str,
        days: int = 90
    ) -> CategoryTrendResponse:
        """Get historical trend and forecast for category"""
        
        # Generate historical data points
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        historical_data = self._generate_historical_trend(
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        
        # Generate forecast data points
        forecast_start = end_date + timedelta(days=1)
        forecast_end = forecast_start + timedelta(days=30)
        
        forecast_data = self._generate_forecast_trend(
            category=category,
            start_date=forecast_start,
            end_date=forecast_end
        )
        
        # Calculate statistics
        actual_sales = [d.actual_sales for d in historical_data if d.actual_sales]
        statistics = {
            "mean": float(np.mean(actual_sales)) if actual_sales else 0,
            "std": float(np.std(actual_sales)) if actual_sales else 0,
            "min": float(np.min(actual_sales)) if actual_sales else 0,
            "max": float(np.max(actual_sales)) if actual_sales else 0,
            "trend": "increasing"  # Simplified
        }
        
        return CategoryTrendResponse(
            category=category,
            historical_data=historical_data,
            forecast_data=forecast_data,
            statistics=statistics
        )
    
    # Private helper methods
    
    def _get_all_categories(self) -> List[str]:
        """Get list of all available categories"""
        return [
            "Electronics",
            "Clothing & Apparel",
            "Home & Garden",
            "Sports & Outdoors",
            "Books & Media",
            "Food & Beverages",
            "Health & Beauty",
            "Toys & Games"
        ]
    
    async def _forecast_category(
        self,
        category: str,
        time_period: str,
        include_confidence: bool
    ) -> CategoryForecast:
        """Generate forecast for single category"""
        
        # Mock data for demo - in production, this would use the ML model
        top_products = await self._get_top_products_for_category(
            category=category,
            time_period=time_period,
            limit=5
        )
        
        total_sales = sum(p.predicted_sales for p in top_products)
        total_revenue = sum(p.predicted_revenue for p in top_products)
        
        # Determine trend (mock logic)
        trend = np.random.choice(["increasing", "stable", "decreasing"], p=[0.6, 0.3, 0.1])
        growth_rate = np.random.uniform(-5, 25) if trend == "increasing" else np.random.uniform(-10, 5)
        
        return CategoryForecast(
            category=category,
            total_predicted_sales=total_sales,
            total_predicted_revenue=total_revenue,
            top_products=top_products,
            trend=trend,
            growth_rate=round(growth_rate, 2)
        )
    
    async def _get_top_products_for_category(
        self,
        category: str,
        time_period: str,
        limit: int
    ) -> List[ProductForecast]:
        """Get top products for a category"""
        
        # Mock product data - in production, load from database/model
        base_products = self._get_mock_products(category)
        
        products = []
        for i, product_name in enumerate(base_products[:limit]):
            # Generate mock predictions
            base_sales = np.random.uniform(100, 1000)
            base_price = np.random.uniform(20, 500)
            
            # Scale by time period
            multiplier = {'week': 1, 'month': 4, 'year': 48}[time_period]
            predicted_sales = base_sales * multiplier
            predicted_revenue = predicted_sales * base_price
            
            # Confidence intervals
            confidence_lower = predicted_sales * 0.85
            confidence_upper = predicted_sales * 1.15
            
            # Trend
            trend = np.random.choice(["increasing", "stable", "decreasing"], p=[0.5, 0.3, 0.2])
            change_percent = np.random.uniform(-10, 30) if trend == "increasing" else np.random.uniform(-15, 10)
            
            products.append(ProductForecast(
                product_id=f"PROD-{category[:3].upper()}-{i+1:03d}",
                product_name=product_name,
                category=category,
                predicted_sales=round(predicted_sales, 2),
                predicted_revenue=round(predicted_revenue, 2),
                confidence_lower=round(confidence_lower, 2),
                confidence_upper=round(confidence_upper, 2),
                trend=trend,
                change_percent=round(change_percent, 2)
            ))
        
        return products
    
    def _get_mock_products(self, category: str) -> List[str]:
        """Get mock product names for category"""
        products_by_category = {
            "Electronics": [
                "Wireless Headphones Pro",
                "Smart Watch Ultra",
                "Laptop 15-inch",
                "4K Monitor 27-inch",
                "Wireless Keyboard",
                "USB-C Hub",
                "Portable SSD 1TB",
                "Webcam HD"
            ],
            "Clothing & Apparel": [
                "Premium Cotton T-Shirt",
                "Slim Fit Jeans",
                "Running Shoes",
                "Winter Jacket",
                "Casual Sneakers",
                "Cotton Hoodie",
                "Yoga Pants",
                "Dress Shirt"
            ],
            "Home & Garden": [
                "Robot Vacuum",
                "Air Purifier",
                "Smart Thermostat",
                "LED Desk Lamp",
                "Garden Tool Set",
                "Storage Bins Set",
                "Coffee Maker",
                "Bed Sheets Set"
            ],
            "Sports & Outdoors": [
                "Yoga Mat Premium",
                "Dumbbell Set",
                "Camping Tent 4-Person",
                "Mountain Bike",
                "Fitness Tracker",
                "Hiking Backpack",
                "Water Bottle",
                "Running Belt"
            ],
            "Books & Media": [
                "Bestseller Fiction Novel",
                "Business Strategy Guide",
                "Cookbook Collection",
                "Biography Series",
                "Self-Help Book",
                "Children's Picture Book",
                "Audio Book Bundle",
                "Magazine Subscription"
            ],
            "Food & Beverages": [
                "Organic Coffee Beans",
                "Protein Powder",
                "Energy Bars Box",
                "Green Tea Set",
                "Olive Oil Premium",
                "Snack Mix Variety",
                "Vitamin Supplements",
                "Meal Replacement Shake"
            ],
            "Health & Beauty": [
                "Skincare Set",
                "Electric Toothbrush",
                "Hair Dryer Pro",
                "Facial Cleanser",
                "Moisturizer Cream",
                "Perfume 50ml",
                "Makeup Kit",
                "Body Lotion"
            ],
            "Toys & Games": [
                "Building Blocks Set",
                "Board Game Classic",
                "Action Figure Collection",
                "Puzzle 1000 Pieces",
                "Remote Control Car",
                "Plush Toy",
                "Card Game Set",
                "Educational STEM Kit"
            ]
        }
        return products_by_category.get(category, ["Product 1", "Product 2", "Product 3"])
    
    def _generate_historical_trend(
        self,
        category: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[TrendDataPoint]:
        """Generate historical trend data points"""
        
        data_points = []
        current_date = start_date
        base_sales = np.random.uniform(500, 2000)
        
        while current_date <= end_date:
            # Add trend and seasonality
            days_elapsed = (current_date - start_date).days
            trend = days_elapsed * 2  # Upward trend
            seasonality = 200 * np.sin(2 * np.pi * days_elapsed / 30)  # Monthly seasonality
            noise = np.random.normal(0, 50)
            
            actual_sales = base_sales + trend + seasonality + noise
            actual_sales = max(0, actual_sales)  # No negative sales
            
            data_points.append(TrendDataPoint(
                date=current_date.strftime("%Y-%m-%d"),
                actual_sales=round(actual_sales, 2)
            ))
            
            current_date += timedelta(days=1)
        
        return data_points
    
    def _generate_forecast_trend(
        self,
        category: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[TrendDataPoint]:
        """Generate forecast trend data points"""
        
        data_points = []
        current_date = start_date
        base_sales = np.random.uniform(800, 2500)
        
        while current_date <= end_date:
            days_elapsed = (current_date - start_date).days
            trend = days_elapsed * 3  # Continuing upward trend
            seasonality = 200 * np.sin(2 * np.pi * days_elapsed / 30)
            
            predicted_sales = base_sales + trend + seasonality
            predicted_sales = max(0, predicted_sales)
            
            # Confidence intervals
            confidence_lower = predicted_sales * 0.85
            confidence_upper = predicted_sales * 1.15
            
            data_points.append(TrendDataPoint(
                date=current_date.strftime("%Y-%m-%d"),
                predicted_sales=round(predicted_sales, 2),
                confidence_lower=round(confidence_lower, 2),
                confidence_upper=round(confidence_upper, 2)
            ))
            
            current_date += timedelta(days=1)
        
        return data_points
