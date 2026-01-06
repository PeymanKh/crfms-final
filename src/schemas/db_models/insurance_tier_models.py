"""
MongoDB document schemas for insurance tier persistence.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class InsuranceTierDocument(BaseModel):
    """
    MongoDB document schema for insurance_tiers collection.

    Collection: insurance_tiers

    Attributes:
        id (str): MongoDB document ID (tier ID).
        tier_name (str): Insurance tier name.
        description (str): Coverage description.
        price_per_day (float): Daily insurance price.
        created_at (datetime): When tier was created.
        updated_at (datetime): Last modification timestamp.
    """

    id: str = Field(..., alias="_id", description="Tier unique identifier")
    tier_name: str
    description: str
    price_per_day: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "indexes": [
                {"keys": [("tier_name", 1)]},
                {"keys": [("created_at", -1)]},
            ]
        },
    )
