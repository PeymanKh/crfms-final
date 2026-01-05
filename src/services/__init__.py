"""
This module provides public API for services singleton instances.
Author: Peyman Khodabandehlouei
"""

# Import modules
from services.auth_service import auth_service


# Public API
__all__ = [
    "auth_service",
]
