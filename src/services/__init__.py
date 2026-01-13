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

# Import add-on service
from services.add_on_service import add_on_service

# Import insurance tier service
from services.insurance_tier_service import insurance_tier_service

# Import reservation service
from services.reservation_service import reservation_service

# Import payment service
from services.payment_service import payment_service

# Import rental service
from services.rental_service import rental_service

# Import event consumer
from services.event_consumer import event_consumer


# Public API
__all__ = [
    "auth_service",
    "branch_service",
    "vehicle_service",
    "add_on_service",
    "insurance_tier_service",
    "reservation_service",
    "payment_service",
    "rental_service",
    "event_consumer",
]
