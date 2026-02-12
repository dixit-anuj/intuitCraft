"""
Forecasting API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.services.forecast_service import ForecastService
from app.models.schemas import (
    ForecastRequest,
    ForecastResponse,
    TopProductsResponse,
    CategoryForecast
)

router = APIRouter()
forecast_service = ForecastService()


@router.post("/predict", response_model=ForecastResponse)
async def predict_sales(request: ForecastRequest):
    """
    Predict sales for specified time period and categories
    
    Args:
        request: Forecast request with time period and categories
    
    Returns:
        Forecast predictions with confidence intervals
    """
    try:
        predictions = await forecast_service.generate_forecast(request)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-products", response_model=TopProductsResponse)
async def get_top_products(
    time_period: str = Query(..., description="Time period: week, month, year"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=100, description="Number of top products")
):
    """
    Get top-selling products by category for a time period
    
    Args:
        time_period: Time period for forecast (week, month, year)
        category: Optional category filter
        limit: Number of top products to return
    
    Returns:
        List of top products with predicted sales
    """
    try:
        top_products = await forecast_service.get_top_products(
            time_period=time_period,
            category=category,
            limit=limit
        )
        return top_products
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=List[CategoryForecast])
async def get_category_forecasts(
    time_period: str = Query(..., description="Time period: week, month, year")
):
    """
    Get sales forecasts for all categories
    
    Args:
        time_period: Time period for forecast (week, month, year)
    
    Returns:
        List of category forecasts with trends
    """
    try:
        category_forecasts = await forecast_service.get_category_forecasts(
            time_period=time_period
        )
        return category_forecasts
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/{category}")
async def get_category_trend(
    category: str,
    days: int = Query(90, ge=7, le=365, description="Historical days to analyze")
):
    """
    Get historical trend and future forecast for a specific category
    
    Args:
        category: Product category
        days: Number of historical days to include
    
    Returns:
        Historical data and forecast
    """
    try:
        trend_data = await forecast_service.get_category_trend(
            category=category,
            days=days
        )
        return trend_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info")
async def get_model_info():
    """
    Get information about the forecasting model
    
    Returns:
        Model metadata, version, and performance metrics
    """
    model = forecast_service.model
    is_loaded = model is not None and model.is_trained
    
    return {
        "model_type": "Ensemble (XGBoost + Holt-Winters)",
        "version": "3.0.0",
        "is_loaded": is_loaded,
        "num_features": len(model.feature_cols) if is_loaded else 0,
        "num_categories": len(model.category_encodings) if is_loaded else 0,
        "performance": {
            "holdout_r2": 0.96,
            "mae_pct": 4.1,
            "mape": 4.3,
            "xgb_train_r2": 0.999,
            "xgb_val_r2": 0.978,
        },
        "training_data": {
            "records": 5848,
            "days": 730,
            "categories": 8,
        },
        "feature_groups": [
            "Cyclical time encoding (sin/cos)",
            "Lag features (7, 14, 30 days)",
            "Rolling statistics (mean, std)",
            "Momentum features",
            "Trend and interaction features",
        ],
    }
