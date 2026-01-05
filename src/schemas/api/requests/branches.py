"""
Request schemas for branch endpoints.

This module contains Pydantic models for branch-related API requests.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from typing import Optional
from pydantic import BaseModel, Field


class CreateBranchRequest(BaseModel):
    """
    Request body for creating a new branch.

    Used by endpoint:
        - POST /api/v1/branches

    Attributes:
        name (str): Branch name.
        city (str): City where branch is located.
        address (str): Full street address.
        phone_number (str): Contact phone number.
    """

    name: str = Field(..., min_length=2, max_length=100, description="Branch name")
    city: str = Field(..., min_length=2, max_length=50, description="City name")
    address: str = Field(..., min_length=5, max_length=200, description="Full address")
    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=20,
        description="Contact phone number",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Istanbul Merkez",
                "city": "Istanbul",
                "address": "Taksim Square, Beyoğlu, Istanbul, Turkey",
                "phone_number": "+905551234567",
            }
        }
    }


class UpdateBranchRequest(BaseModel):
    """
    Request body for updating branch information.

    Used by endpoint:
        - PUT /api/v1/branches/{branch_id}

    Attributes:
        name (Optional[str]): Branch name.
        city (Optional[str]): City name.
        address (Optional[str]): Full address.
        phone_number (Optional[str]): Contact phone number.
    """

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    city: Optional[str] = Field(None, min_length=2, max_length=50)
    address: Optional[str] = Field(None, min_length=5, max_length=200)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)

    model_config = {
        "json_schema_extra": {
            "example": {
                "phone_number": "+905559876543",
                "address": "Kadıköy, Istanbul, Turkey",
            }
        }
    }
