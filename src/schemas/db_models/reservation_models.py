"""
MongoDB document schemas for reservation persistence.

Author: Peyman Khodabandehlouei
Date: 06-01-2026
"""

from datetime import datetime, date
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class ReservationAddOnDocument(BaseModel):
    """
    Embedded add-on document schema within reservations.

    This stores a snapshot of the add-on at the time of reservation,
    preserving historical pricing even if the add-on is updated later.

    Attributes:
        id (str): Add-on unique identifier (reference to add_ons collection).
        name (str): Add-on name (snapshot at reservation time).
        price_per_day (float): Daily price (snapshot at reservation time).
    """

    id: str
    name: str
    price_per_day: float

    model_config = ConfigDict(populate_by_name=True)


class ReservationDocument(BaseModel):
    """
    MongoDB document schema for reservations collection.

    Collection: reservations

    This document stores both reference IDs (for relationships) and
    embedded add-on details (for historical pricing integrity).

    Attributes:
        _id (str): MongoDB document ID (reservation ID).
        status (str): Reservation status (pending/confirmed/cancelled/completed).
        customer_id (str): ID of customer who made reservation (FK to customers).
        vehicle_id (str): ID of reserved vehicle (FK to vehicles).
        insurance_tier_id (str): ID of insurance tier (FK to insurance_tiers).
        pickup_branch_id (str): Branch ID for pickup (FK to branches).
        return_branch_id (str): Branch ID for return (FK to branches).
        pickup_date (date): Date when vehicle will be picked up.
        return_date (date): Date when vehicle will be returned.
        add_ons (List[ReservationAddOnDocument]): List of add-ons with snapshot pricing.
        total_price (float): Calculated total price (vehicle + insurance + add-ons × days).
        rental_days (int): Number of rental days (return_date - pickup_date).
        created_at (datetime): When reservation was created.
        updated_at (datetime): Last modification timestamp.
    """

    id: str = Field(..., alias="_id", description="Reservation unique identifier")
    status: str
    customer_id: str
    vehicle_id: str
    insurance_tier_id: str
    pickup_branch_id: str
    return_branch_id: str
    pickup_date: date
    return_date: date
    add_ons: List[ReservationAddOnDocument] = Field(default_factory=list)
    total_price: float
    rental_days: int
    created_at: datetime
    updated_at: datetime
