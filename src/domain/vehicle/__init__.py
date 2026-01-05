"""
This module provides public API for Vehicle domain including Vehicle,
VehicleClass, and MaintenanceRecord.

Author: Peyman Khodabandehlouei
"""

# Import modules
from domain.vehicle.vehicle import Vehicle
from domain.vehicle.vehicle_class import VehicleClass
from domain.vehicle.maintenance_record import MaintenanceRecord


# Public API
__all__ = [
    "Vehicle",
    "VehicleClass",
    "MaintenanceRecord",
]
