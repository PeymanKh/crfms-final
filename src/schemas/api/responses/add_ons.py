"""
Response schemas for add-on endpoints.

This module contains Pydantic models for add-on-related API responses.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class AddOnData(BaseModel):
    """
    Add-on data payload for API responses.

    Used in:
        - POST /api/v1/add-ons (create response)
        - GET /api/v1/add-ons/{id} (get response)
        - PUT /api/v1/add-ons/{id} (update response)
        - GET /api/v1/add-ons (list of items)

    Attributes:
        id (str): Unique add-on identifier.
        name (str): Add-on name.
        description (str): Add-on description.
        price_per_day (float): Daily rental price.
        created_at (datetime): When add-on was created.
        updated_at (datetime): Last update timestamp.
    """

    id: str = Field(..., description="Unique add-on identifier")
    name: str = Field(..., description="Add-on name")
    description: str = Field(..., description="Description")
    price_per_day: float = Field(..., description="Daily price")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "addon-uuid-123",
                "name": "GPS Navigation System",
                "description": "Premium GPS with real-time traffic updates",
                "price_per_day": 5.0,
                "created_at": "2026-01-05T18:00:00Z",
                "updated_at": "2026-01-05T18:00:00Z",
            }
        },
    )


class AddOnListData(BaseModel):
    """
    Response data for add-on list endpoint.

    Used by:
        - GET /api/v1/add-ons

    Attributes:
        add_ons (List[AddOnData]): List of add-ons.
        total_count (int): Total number of add-ons.
    """

    add_ons: List[AddOnData] = Field(..., description="List of add-ons")
    total_count: int = Field(..., description="Total add-ons count")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "add_ons": [
                    {
                        "id": "addon-uuid-123",
                        "name": "GPS Navigation System",
                        "description": "Premium GPS with real-time traffic updates",
                        "price_per_day": 5.0,
                        "created_at": "2026-01-05T18:00:00Z",
                        "updated_at": "2026-01-05T18:00:00Z",
                    }
                ],
                "total_count": 1,
            }
        }
    )
