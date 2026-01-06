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

# Import add-on schemas
from schemas.api.responses.add_ons import AddOnData, AddOnListData

# Import insurance tier schemas
from schemas.api.responses.insurance_tiers import (
    InsuranceTierData,
    InsuranceTierListData,
)

# Import reservation schemas
from schemas.api.responses.reservations import (
    ReservationAddOnData,
    ReservationData,
    ReservationListData,
    InvoiceData,
)


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
    # add-on schemas
    "AddOnData",
    "AddOnListData",
    # insurance tier schemas
    "InsuranceTierData",
    "InsuranceTierListData",
    # reservation schemas
    "ReservationData",
    "ReservationListData",
    "ReservationAddOnData",
    "InvoiceData",
]
