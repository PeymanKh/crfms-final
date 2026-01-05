"""
This module provides public API for API request schemas.
Author: Peyman Khodabandehlouei
"""

# Import modules
from schemas.api.requests.auth import (
    CustomerRegistrationRequest,
    AgentRegistrationRequest,
    ManagerRegistrationRequest,
)


# Public API
__all__ = [
    "CustomerRegistrationRequest",
    "AgentRegistrationRequest",
    "ManagerRegistrationRequest",
]
