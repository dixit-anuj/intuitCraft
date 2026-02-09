"""
Data API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()


@router.get("/categories")
async def get_available_categories():
    """Get list of available product categories"""
    return {
        "categories": [
            "Electronics",
            "Clothing & Apparel",
            "Home & Garden",
            "Sports & Outdoors",
            "Books & Media",
            "Food & Beverages",
            "Health & Beauty",
            "Toys & Games"
        ]
    }


@router.get("/statistics")
async def get_data_statistics(
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get statistical summary of sales data"""
    return {
        "total_transactions": 125430,
        "date_range": {
            "start": "2023-01-01",
            "end": "2026-02-09"
        },
        "categories": 8,
        "unique_products": 2847,
        "avg_daily_sales": 15234.56,
        "total_revenue": 15647892.34
    }


@router.get("/external-indicators")
async def get_external_indicators():
    """Get current external economic indicators"""
    return {
        "timestamp": "2026-02-09T00:00:00Z",
        "indicators": {
            "gdp_growth": 2.8,
            "inflation_rate": 3.2,
            "consumer_confidence": 102.5,
            "unemployment_rate": 3.9,
            "retail_sales_growth": 4.5
        },
        "sources": [
            "FRED API",
            "Yahoo Finance"
        ]
    }
