"""
Response schemas for vehicle endpoints.

This module contains Pydantic models for vehicle-related API responses.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class VehicleData(BaseModel):
    """
    Vehicle data payload for API responses.

    Used in:
        - POST /api/v1/vehicles (create response)
        - GET /api/v1/vehicles/{id} (get response)
        - PUT /api/v1/vehicles/{id} (update response)
        - GET /api/v1/vehicles (list response - array of this)

    Attributes:
        id (str): Unique vehicle identifier.
        plate_number (str): License plate number.
        brand (str): Vehicle brand.
        model (str): Vehicle model.
        year (int): Manufacturing year.
        vehicle_class (str): Class category.
        price_per_day (float): Daily rental rate.
        mileage (float): Current odometer reading.
        branch_id (str): Branch location.
        status (str): Current status.
        created_at (datetime): When vehicle was added.
        updated_at (datetime): Last update timestamp.
    """

    id: str = Field(..., description="Unique vehicle identifier")
    plate_number: str = Field(..., description="License plate number")
    brand: str = Field(..., description="Vehicle brand")
    model: str = Field(..., description="Vehicle model")
    year: int = Field(..., description="Manufacturing year")
    vehicle_class: str = Field(..., description="Vehicle class")
    price_per_day: float = Field(..., description="Daily rental rate")
    mileage: float = Field(..., description="Odometer reading (km)")
    branch_id: str = Field(..., description="Branch ID")
    status: str = Field(..., description="Vehicle status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "vehicle-uuid-123",
                "plate_number": "34ABC123",
                "brand": "Toyota",
                "model": "Corolla",
                "year": 2023,
                "vehicle_class": "economy",
                "price_per_day": 45.0,
                "mileage": 15000.0,
                "branch_id": "branch-istanbul-1",
                "status": "available",
                "created_at": "2026-01-05T11:00:00Z",
                "updated_at": "2026-01-05T11:00:00Z",
            }
        },
    )


class VehicleListData(BaseModel):
    """
    Response data for vehicle list endpoint.

    Used by:
        GET /api/v1/vehicles

    Attributes:
        vehicles (List[VehicleData]): List of vehicles.
        total_count (int): Total number of vehicles matching filters.
    """

    vehicles: List[VehicleData] = Field(..., description="List of vehicles")
    total_count: int = Field(..., description="Total vehicles count")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vehicles": [
                    {
                        "id": "vehicle-uuid-123",
                        "plate_number": "34ABC123",
                        "brand": "Toyota",
                        "model": "Corolla",
                        "year": 2023,
                        "vehicle_class": "economy",
                        "price_per_day": 45.0,
                        "mileage": 15000.0,
                        "branch_id": "branch-istanbul-1",
                        "status": "available",
                        "created_at": "2026-01-05T11:00:00Z",
                        "updated_at": "2026-01-05T11:00:00Z",
                    }
                ],
                "total_count": 1,
            }
        }
    )
