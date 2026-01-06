"""
MongoDB document schemas for add-on persistence.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AddOnDocument(BaseModel):
    """
    MongoDB document schema for add_ons collection.

    Collection: add_ons

    Attributes:
        id (str): MongoDB document ID (add-on ID).
        name (str): Add-on name.
        description (str): Add-on description.
        price_per_day (float): Daily rental price.
        created_at (datetime): When add-on was created.
        updated_at (datetime): Last modification timestamp.
    """

    id: str = Field(..., alias="_id", description="Add-on unique identifier")
    name: str
    description: str
    price_per_day: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "indexes": [
                {"keys": [("name", 1)]},
                {"keys": [("created_at", -1)]},
            ]
        },
    )
