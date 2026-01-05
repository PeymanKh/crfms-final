"""
This module provides public API for API request schemas.
Author: Peyman Khodabandehlouei
"""

# Import auth schemas
from schemas.api.requests.auth import (
    CustomerRegistrationRequest,
    AgentRegistrationRequest,
    ManagerRegistrationRequest,
)

# Import vehicle schemas
from schemas.api.requests.vehicles import (
    VehicleClassType,
    CreateVehicleRequest,
    UpdateVehicleRequest,
    VehicleFilterRequest,
)

# Import branch schemas
from schemas.api.requests.branches import CreateBranchRequest, UpdateBranchRequest


# Public API
__all__ = [
    # auth schemas
    "CustomerRegistrationRequest",
    "AgentRegistrationRequest",
    "ManagerRegistrationRequest",
    # vehicle schemas
    "CreateVehicleRequest",
    "UpdateVehicleRequest",
    "VehicleFilterRequest",
    "VehicleClassType",
    # branch schemas
    "CreateBranchRequest",
    "UpdateBranchRequest",
]
