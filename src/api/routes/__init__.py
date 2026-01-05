"""
This module provides the public API for API routes.

Public API:
    3. health_check_router

Author: Peyman Khodabandehlouei
Last Update: 28-12-2025
"""

from api.routes.health import router as health_router
from api.routes.auth import router as auth_router
from api.routes.vehicle import router as vehicle_router


# Public API
__all__ = [
    "health_router",
    "auth_router",
    "vehicle_router",
]
