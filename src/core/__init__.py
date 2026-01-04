"""
This module provides public API for custom errors in the application

Author: Peyman Khodabandehlouei
"""

# Import modules
from core.clock_service import ClockService, SystemClock, FakeClock

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
    "FakeClock",
    "SystemClock",
    "ClockService",
    "ReservationNotFoundError",
    "VehicleNotAvailableError",
    "ReservationNotApprovedError",
    "PaymentRequiredForPickupError",
    "ReturnDateBeforePickupDateError",
    "InvalidReservationStatusForCancellationError",
]
