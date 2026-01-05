"""
This module provides public API for db_models.
Author: Peyman Khodabandehlouei
"""

# Import auth schemas
from schemas.db_models.auth_models import CustomerDocument, EmployeeDocument

# Import vehicles schemas
from schemas.db_models.vehicle_models import VehicleDocument

# Import branch schemas
from schemas.db_models.branch_models import BranchDocument


# Public API
__all__ = [
    # auth schemas
    "CustomerDocument",
    "EmployeeDocument",
    # vehicle schemas
    "VehicleDocument",
    # branch schemas
    "BranchDocument",
]
