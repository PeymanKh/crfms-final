"""
This module provides public API for Vehicle entities including Vehicle,
VehicleClass, and MaintenanceRecord.

Author: Peyman Khodabandehlouei
"""

# Import modules
from entities.vehicle.vehicle import Vehicle
from entities.vehicle.vehicle_class import VehicleClass
from entities.vehicle.maintenance_record import MaintenanceRecord


# Public API
__all__ = [
    "Vehicle",
    "VehicleClass",
    "MaintenanceRecord",
]
