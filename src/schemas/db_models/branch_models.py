"""
MongoDB document schemas for branch persistence.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class BranchDocument(BaseModel):
    """
    MongoDB document schema for branches collection.

    Collection: branches

    Attributes:
        id (str): MongoDB document ID (branch ID).
        name (str): Branch name.
        city (str): City where branch is located.
        address (str): Full street address.
        phone_number (str): Contact phone number.
        employee_ids (List[str]): List of employee IDs working at this branch.
        created_at (datetime): When branch was created.
        updated_at (datetime): Last modification timestamp.
    """

    id: str = Field(..., alias="_id", description="Branch unique identifier")
    name: str
    city: str
    address: str
    phone_number: str
    employee_ids: List[str] = Field(
        default_factory=list, description="Employee IDs at this branch"
    )
    created_at: datetime
    updated_at: datetime
