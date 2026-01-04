"""
Health check API endpoint.

This module defines a health check route used to verify that the service
is running, configuration is valid, and external dependencies are accessible.

Author: Peyman Khodabandehlouei
Last Update: 29-12-2025
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, status, Response

from core import config, db_manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Service health check",
    description="Check service health including configuration and database connectivity",
)
async def health_check(response: Response) -> Dict[str, Any]:
    """
    Health check for the service.

    Checks:
        - Required environment variables/configuration
        - Database connectivity

    Returns:
        dict: Health status with component details

    Response Codes:
        - 200: All components healthy
        - 503: One or more components are unhealthy
    """

    health_status = {
        "status": "healthy",
        "checks": {
            "config": {"status": "unknown"},
            "database": {"status": "unknown"},
        },
    }

    # Check environment variables
    config_check = await _check_config()
    health_status["checks"]["config"] = config_check

    # Check database connectivity
    db_check = await _check_database()
    health_status["checks"]["database"] = db_check

    # Determine overall status
    all_healthy = all(
        check["status"] == "healthy" for check in health_status["checks"].values()
    )

    if not all_healthy:
        health_status["status"] = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        logger.warning(f"Health check failed. {health_status}")
    else:
        logger.debug("Health check passed")

    return health_status


async def _check_config() -> Dict[str, Any]:
    """
    Validate required configuration is present.

    Returns:
        dict: Config check result with status and details
    """
    missing_vars = []

    try:
        # Check database config
        if not config.database.uri.get_secret_value():
            missing_vars.append("DATABASE_URI")

        # Check RabbitMQ config
        if not config.rabbitmq.url.get_secret_value():
            missing_vars.append("RABBITMQ_URL")

        if not config.database.name:
            missing_vars.append("DATABASE_NAME")

        if missing_vars:
            return {
                "status": "unhealthy",
                "message": "Missing required configuration. Please check .env file",
                "missing_variables": missing_vars,
            }

        return {
            "status": "healthy",
            "message": "All required configuration are present in .env file",
        }

    except Exception as e:
        logger.error(f"Config check failed. error={str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "message": "Failed to read configuration",
            "error": str(e),
        }


async def _check_database() -> Dict[str, Any]:
    """
    Check database connectivity.

    Returns:
        dict: Database check result with status and details
    """
    try:
        is_healthy = await db_manager.health_check()

        if is_healthy:
            return {"status": "healthy", "message": "Database connection is active"}
        else:
            return {"status": "unhealthy", "message": "Database connection failed"}

    except Exception as e:
        logger.error(f"Database check failed. error={str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "message": "Database health check error",
            "error": str(e),
        }
