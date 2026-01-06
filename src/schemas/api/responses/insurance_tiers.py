"""
Response schemas for insurance tier endpoints.

This module contains Pydantic models for insurance-tier-related API responses.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class InsuranceTierData(BaseModel):
    """
    Insurance tier data payload for API responses.

    Used in:
        - POST /api/v1/insurance-tiers (create response)
        - GET /api/v1/insurance-tiers/{id} (get response)
        - PUT /api/v1/insurance-tiers/{id} (update response)
        - GET /api/v1/insurance-tiers (list of items)

    Attributes:
        id (str): Unique insurance tier identifier.
        tier_name (str): Tier name.
        description (str): Coverage description.
        price_per_day (float): Daily insurance price.
        created_at (datetime): When tier was created.
        updated_at (datetime): Last update timestamp.
    """

    id: str = Field(..., description="Unique tier identifier")
    tier_name: str = Field(..., description="Tier name")
    description: str = Field(..., description="Coverage description")
    price_per_day: float = Field(..., description="Daily price")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "tier-uuid-123",
                "tier_name": "Premium Coverage",
                "description": "Full coverage with zero deductible",
                "price_per_day": 25.0,
                "created_at": "2026-01-05T18:00:00Z",
                "updated_at": "2026-01-05T18:00:00Z",
            }
        },
    )


class InsuranceTierListData(BaseModel):
    """
    Response data for insurance tier list endpoint.

    Used by:
        - GET /api/v1/insurance-tiers

    Attributes:
        insurance_tiers (List[InsuranceTierData]): List of insurance tiers.
        total_count (int): Total number of tiers.
    """

    insurance_tiers: List[InsuranceTierData] = Field(..., description="List of tiers")
    total_count: int = Field(..., description="Total tiers count")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "insurance_tiers": [
                    {
                        "id": "tier-uuid-123",
                        "tier_name": "Premium Coverage",
                        "description": "Full coverage with zero deductible",
                        "price_per_day": 25.0,
                        "created_at": "2026-01-05T18:00:00Z",
                        "updated_at": "2026-01-05T18:00:00Z",
                    }
                ],
                "total_count": 1,
            }
        }
    )
