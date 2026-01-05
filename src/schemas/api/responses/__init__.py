"""
This module provides public API for API responses schemas.
Author: Peyman Khodabandehlouei
"""

# Import auth schemas
from schemas.api.responses.auth import CustomerData, EmployeeData

# Import vehicles schemas
from schemas.api.responses.vehicles import VehicleData, VehicleListData

# Import branch schemas
from schemas.api.responses.branches import BranchData, BranchListData

# Public API
__all__ = [
    # auth schemas
    "CustomerData",
    "EmployeeData",
    # vehicle schemas
    "VehicleData",
    "VehicleListData",
    # branch schemas
    "BranchData",
    "BranchListData",
]
