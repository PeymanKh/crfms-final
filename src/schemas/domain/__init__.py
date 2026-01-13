"""
This module provides public API for application's entity schemas.

Author: Peyman Khodabandehlouei
"""

# Import modules
from schemas.domain.schemas import RentalCharges, RentalReading
from schemas.domain.events import DomainEvent, EventTypes
from schemas.domain.enums import (
    Gender,
    EmploymentType,
    VehicleStatus,
    ReservationStatus,
    InvoiceStatus,
    RentalStatus,
)


# Public API
__all__ = [
    "Gender",
    "InvoiceStatus",
    "VehicleStatus",
    "EmploymentType",
    "ReservationStatus",
    "RentalCharges",
    "RentalReading",
    "RentalStatus",
    "DomainEvent",
    "EventTypes",
]
