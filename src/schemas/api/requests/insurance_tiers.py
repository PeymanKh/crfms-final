"""
Request schemas for insurance tier endpoints.

This module contains Pydantic models for insurance-tier-related API requests.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from typing import Optional
from pydantic import BaseModel, Field


class CreateInsuranceTierRequest(BaseModel):
    """
    Request body for creating a new insurance tier.

    Used by endpoint:
        - POST /api/v1/insurance-tiers

    Attributes:
        tier_name (str): Insurance tier name (e.g., "Basic", "Standard", "Premium").
        description (str): Detailed description of coverage.
        price_per_day (float): Daily insurance price.
    """

    tier_name: str = Field(..., min_length=2, max_length=50, description="Tier name")
    description: str = Field(
        ..., min_length=10, max_length=500, description="Coverage description"
    )
    price_per_day: float = Field(
        ..., ge=0, description="Daily price (must be non-negative)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tier_name": "Premium Coverage",
                "description": "Full coverage with zero deductible, roadside assistance, and rental car replacement",
                "price_per_day": 25.0,
            }
        }
    }


class UpdateInsuranceTierRequest(BaseModel):
    """
    Request body for updating insurance tier information.

    Used by endpoint:
        - PUT /api/v1/insurance-tiers/{tier_id}

    Attributes:
        tier_name (Optional[str]): New tier name.
        description (Optional[str]): New description.
        price_per_day (Optional[float]): New daily price.
    """

    tier_name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    price_per_day: Optional[float] = Field(None, ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "price_per_day": 27.0,
                "description": "Updated: Full coverage with enhanced roadside assistance",
            }
        }
    }
