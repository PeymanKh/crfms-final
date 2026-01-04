"""
This module provides public API for custom errors in the application

Author: Peyman Khodabandehlouei
"""

# Import modules
from core.exceptions import (
    ReturnDateBeforePickupDateError,
    InvalidReservationStatusForCancellationError,
    PaymentRequiredForPickupError,
    ReservationNotApprovedError,
    ReservationNotFoundError,
    VehicleNotAvailableError,
)

# Public API
__all__ = [
    "ReservationNotFoundError",
    "VehicleNotAvailableError",
    "ReservationNotApprovedError",
    "PaymentRequiredForPickupError",
    "ReturnDateBeforePickupDateError",
    "InvalidReservationStatusForCancellationError",
]
