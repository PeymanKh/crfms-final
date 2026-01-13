"""
This module provides public API for custom errors in the application

Author: Peyman Khodabandehlouei
"""

# Import configs
from core.config import config
from core.logging_config import setup_logging

# Import database manager
from core.database_manager import db_manager

# Import rabbitmq manager
from core.rabbitmq_manager import rabbitmq_manager

# Import clock service
from core.clock_service import ClockService, SystemClock, FakeClock

# Import custom errors
from core.exceptions import (
    ReturnDateBeforePickupDateError,
    InvalidReservationStatusForCancellationError,
    PaymentRequiredForPickupError,
    ReservationNotApprovedError,
    ReservationNotFoundError,
    VehicleNotAvailableError,
    ApplicationStartUpError,
    ApplicationShutdownError,
    DuplicateEmailError,
)

# Public API
__all__ = [
    # Configs
    "config",
    "setup_logging",
    # Database
    "db_manager",
    # RabbitMQ
    "rabbitmq_manager",
    # Clock
    "FakeClock",
    "SystemClock",
    "ClockService",
    # Exceptions
    "DuplicateEmailError",
    "ApplicationStartUpError",
    "ApplicationShutdownError",
    "ReservationNotFoundError",
    "VehicleNotAvailableError",
    "ReservationNotApprovedError",
    "PaymentRequiredForPickupError",
    "ReturnDateBeforePickupDateError",
    "InvalidReservationStatusForCancellationError",
]
