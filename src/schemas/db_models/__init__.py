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

# Import add-on schemas
from schemas.db_models.add_on_models import AddOnDocument

# Import insurance tier schemas
from schemas.db_models.insurance_tier_models import InsuranceTierDocument


# Public API
__all__ = [
    # auth schemas
    "CustomerDocument",
    "EmployeeDocument",
    # vehicle schemas
    "VehicleDocument",
    # branch schemas
    "BranchDocument",
    # add-on schemas
    "AddOnDocument",
    # insurance tier schemas
    "InsuranceTierDocument",
]
