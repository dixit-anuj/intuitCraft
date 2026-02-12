"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict
from datetime import datetime


class ForecastRequest(BaseModel):
    """Request schema for forecast predictions"""
    model_config = {
        "json_schema_extra": {
            "example": {
                "time_period": "month",
                "categories": ["Electronics", "Clothing & Apparel"],
                "include_confidence": True
            }
        }
    }

    time_period: str = Field(..., description="Time period: week, month, year")
    categories: Optional[List[str]] = Field(None, description="Specific categories to forecast")
    include_confidence: bool = Field(True, description="Include confidence intervals")


class ProductForecast(BaseModel):
    """Individual product forecast"""
    product_id: str
    product_name: str
    category: str
    predicted_sales: float
    predicted_revenue: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None
    trend: str  # "increasing", "stable", "decreasing"
    change_percent: float


class CategoryForecast(BaseModel):
    """Category-level forecast"""
    category: str
    total_predicted_sales: float
    total_predicted_revenue: float
    top_products: List[ProductForecast]
    trend: str
    growth_rate: float


class ForecastResponse(BaseModel):
    """Response schema for forecast predictions"""
    model_config = {
        "protected_namespaces": (),
        "json_schema_extra": {
            "example": {
                "time_period": "month",
                "forecast_date": "2026-02-09T00:00:00Z",
                "predictions": [],
                "model_version": "1.0.0",
                "accuracy_score": 0.87
            }
        }
    }

    time_period: str
    forecast_date: datetime
    predictions: List[CategoryForecast]
    model_version: str = "1.0.0"
    accuracy_score: float


class TopProductsResponse(BaseModel):
    """Response for top products query"""
    time_period: str
    category: Optional[str]
    products: List[ProductForecast]
    total_count: int
    generated_at: datetime


class TrendDataPoint(BaseModel):
    """Single data point in trend series"""
    date: str
    actual_sales: Optional[float] = None
    predicted_sales: Optional[float] = None
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None


class CategoryTrendResponse(BaseModel):
    """Response for category trend"""
    category: str
    historical_data: List[TrendDataPoint]
    forecast_data: List[TrendDataPoint]
    statistics: Dict[str, Any]
