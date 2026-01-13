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
from api.routes.branches import router as branch_router
from api.routes.add_ons import router as add_ons_router
from api.routes.insurance_tiers import router as insurance_tiers_router
from api.routes.reservations import router as reservation_router
from api.routes.payments import router as payment_router
from api.routes.rentals import router as rental_router

# Public API
__all__ = [
    "health_router",
    "auth_router",
    "vehicle_router",
    "branch_router",
    "add_ons_router",
    "insurance_tiers_router",
    "reservation_router",
    "payment_router",
    "rental_router",
]
