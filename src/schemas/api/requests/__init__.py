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

# Import add-on schemas
from schemas.api.requests.add_ons import CreateAddOnRequest, UpdateAddOnRequest

# Import insurance tier schemas
from schemas.api.requests.insurance_tiers import (
    CreateInsuranceTierRequest,
    UpdateInsuranceTierRequest,
)

# Import reservation schemas
from schemas.api.requests.reservations import (
    CreateReservationRequest,
    UpdateReservationRequest,
    ReservationFilterRequest,
)

# Import payment schemas
from schemas.api.requests.payments import (
    CreditCardPaymentDetails,
    PayPalPaymentDetails,
    ProcessPaymentRequest,
)


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
    # add-on schemas
    "CreateAddOnRequest",
    "UpdateAddOnRequest",
    # insurance tier schemas
    "CreateInsuranceTierRequest",
    "UpdateInsuranceTierRequest",
    # reservation schemas
    "CreateReservationRequest",
    "UpdateReservationRequest",
    "ReservationFilterRequest",
    # payment schemas
    "CreditCardPaymentDetails",
    "PayPalPaymentDetails",
    "ProcessPaymentRequest",
]
