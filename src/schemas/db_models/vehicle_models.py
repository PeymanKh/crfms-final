"""
MongoDB document schemas for vehicle persistence.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import datetime
from pydantic import BaseModel, Field


class VehicleDocument(BaseModel):
    """
    MongoDB document schema for the vehicles collection.

    Collection: vehicles

    Attributes:
        id (str): MongoDB document ID (vehicle ID).
        plate_number (str): License plate number (indexed, unique).
        brand (str): Vehicle brand.
        model (str): Vehicle model.
        year (int): Manufacturing year.
        vehicle_class (str): Class category (economy/standard/luxury/suv).
        price_per_day (float): Daily rental rate.
        mileage (float): Current odometer reading in kilometers.
        branch_id (str): Branch where vehicle is located (indexed).
        status (str): Vehicle status (available/reserved/rented/maintenance).
        created_at (datetime): When vehicle was added to the system.
        updated_at (datetime): Last modification timestamp.
    """

    id: str = Field(..., alias="_id", description="Vehicle unique identifier")
    plate_number: str
    brand: str
    model: str
    year: int
    vehicle_class: str
    price_per_day: float
    mileage: float
    branch_id: str
    status: str
    created_at: datetime
    updated_at: datetime
