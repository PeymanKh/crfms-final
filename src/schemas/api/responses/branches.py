"""
Response schemas for branch endpoints.

This module contains Pydantic models for branch-related API responses.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class BranchData(BaseModel):
    """
    Branch data payload for API responses.

    Used in:
        - POST /api/v1/branches (create response)
        - GET /api/v1/branches/{id} (get response)
        - PUT /api/v1/branches/{id} (update response)
        - GET /api/v1/branches (list of branches)

    Attributes:
        id (str): Unique branch identifier.
        name (str): Branch name.
        city (str): City location.
        address (str): Full street address.
        phone_number (str): Contact phone number.
        employee_count (int): Number of employees at this branch.
        created_at (datetime): When branch was created.
        updated_at (datetime): Last update timestamp.
    """

    id: str = Field(..., description="Unique branch identifier")
    name: str = Field(..., description="Branch name")
    city: str = Field(..., description="City")
    address: str = Field(..., description="Address")
    phone_number: str = Field(..., description="Phone number")
    employee_count: int = Field(..., description="Number of employees")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "branch-uuid-123",
                "name": "Istanbul Central Branch",
                "city": "Istanbul",
                "address": "Taksim Square, Beyoğlu, Istanbul, Turkey",
                "phone_number": "+905551234567",
                "employee_count": 5,
                "created_at": "2026-01-05T15:00:00Z",
                "updated_at": "2026-01-05T15:00:00Z",
            }
        },
    )


class BranchListData(BaseModel):
    """
    Response data for branch list endpoint.

    Used by:
        - GET /api/v1/branches

    Attributes:
        branches (List[BranchData]): List of branches.
        total_count (int): Total number of branches.
    """

    branches: List[BranchData] = Field(..., description="List of branches")
    total_count: int = Field(..., description="Total branches count")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "branches": [
                    {
                        "id": "branch-uuid-123",
                        "name": "Istanbul Central Branch",
                        "city": "Istanbul",
                        "address": "Taksim Square, Beyoğlu, Istanbul, Turkey",
                        "phone_number": "+905551234567",
                        "employee_count": 5,
                        "created_at": "2026-01-05T15:00:00Z",
                        "updated_at": "2026-01-05T15:00:00Z",
                    }
                ],
                "total_count": 1,
            }
        }
    )
