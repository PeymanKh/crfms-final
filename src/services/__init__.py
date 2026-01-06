"""
This module provides public API for services singleton instances.
Author: Peyman Khodabandehlouei
"""

# Import auth service
from services.auth_service import auth_service

# Import branch service
from services.branch_service import branch_service

# Import vehicle service
from services.vehicle_service import vehicle_service

# Public API
__all__ = [
    "auth_service",
    "branch_service",
    "vehicle_service",
]
