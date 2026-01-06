"""
Request schemas for add-on endpoints.

This module contains Pydantic models for add-on-related API requests.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from typing import Optional
from pydantic import BaseModel, Field


class CreateAddOnRequest(BaseModel):
    """
    Request body for creating a new add-on.

    Used by endpoint:
        - POST /api/v1/add-ons

    Attributes:
        name (str): Add-on name (e.g., "GPS Navigation", "Child Seat").
        description (str): Detailed description of the add-on.
        price_per_day (float): Daily rental price for this add-on.
    """

    name: str = Field(..., min_length=2, max_length=100, description="Add-on name")
    description: str = Field(
        ..., min_length=5, max_length=500, description="Add-on description"
    )
    price_per_day: float = Field(
        ..., ge=0, description="Daily price (must be non-negative)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "GPS Navigation System",
                "description": "Premium GPS with real-time traffic updates and offline maps",
                "price_per_day": 5.0,
            }
        }
    }


class UpdateAddOnRequest(BaseModel):
    """
    Request body for updating add-on information.

    Used by endpoint:
        - PUT /api/v1/add-ons/{add_on_id}

    Attributes:
        name (Optional[str]): New add-on name.
        description (Optional[str]): New description.
        price_per_day (Optional[float]): New daily price.
    """

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=5, max_length=500)
    price_per_day: Optional[float] = Field(None, ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "price_per_day": 6.0,
                "description": "Updated: Premium GPS with voice guidance",
            }
        }
    }
