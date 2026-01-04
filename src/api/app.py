"""
FastAPI application entry point.

Author: Peyman Khodabandehlouei
Date: 04-01-2026
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health_router

from core import (
    SystemClock,
    db_manager,
    setup_logging,
    ApplicationShutdownError,
    ApplicationStartUpError,
)


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
        - Startup: Connect to MongoDB
        - Shutdown: Close MongoDB connection and cleanup resources
    """
    logger.info("Starting CRFMS API...")

    try:
        # Connect to MongoDB
        await db_manager.connect()
        logger.info("Database connection established")

        # Initialize clock service
        app.state.clock = SystemClock()
        logger.info("Clock service initialized")

        logger.info("CRFMS API started successfully")

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise ApplicationStartUpError(str(e)) from e

    yield

    # Shutdown
    logger.info("Shutting down CRFMS API...")

    try:
        await db_manager.disconnect()
        logger.info("Database disconnected")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        raise ApplicationShutdownError(str(e)) from e

    logger.info("CRFMS API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Car Rental & Fleet Management System",
    version="1.0.0",
    description="Backend API for CRFMS - Developed by Peyman Khodabandehlouei (2104987)",
    lifespan=lifespan,
    contact={
        "name": "Peyman Khodabandehlouei",
        "url": "https://peymankh.dev",
        "email": "peymankhodabandehlouei@gmail.com",
    },
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
