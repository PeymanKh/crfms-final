"""
This module provides public API for db_models.
Author: Peyman Khodabandehlouei
"""

# Import modules
from schemas.db_models.auth_models import CustomerDocument, EmployeeDocument


# Public API
__all__ = [
    "CustomerDocument",
    "EmployeeDocument",
]
