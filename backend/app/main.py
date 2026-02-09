"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.api import forecasting, health, data
from app.core.config import settings

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")

app = FastAPI(
    title="QuickBooks Commerce Sales Forecasting API",
    description="AI-powered sales forecasting system for e-commerce",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(forecasting.router, prefix="/api/v1/forecast", tags=["Forecasting"])
app.include_router(data.router, prefix="/api/v1/data", tags=["Data"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting QuickBooks Commerce Forecasting API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("API ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down API...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QuickBooks Commerce Sales Forecasting API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
