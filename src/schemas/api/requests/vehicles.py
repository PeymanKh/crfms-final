"""
Request schemas for vehicle endpoints.

This module contains Pydantic models for vehicle-related API requests.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

from schemas.domain import VehicleStatus


# Allowed VehicleClasses
VehicleClassType = Literal["economy", "compact", "suv"]


class CreateVehicleRequest(BaseModel):
    """
    Request body for creating a new vehicle.

    Used by endpoint:
        - POST /api/v1/vehicles

    Attributes:
        plate_number (str): Vehicle license plate number (unique).
        brand (str): Vehicle brand/manufacturer.
        model (str): Vehicle model name.
        year (int): Manufacturing year.
        vehicle_class (str): Class category (economy/standard/luxury/suv).
        price_per_day (float): Daily rental rate.
        mileage (float): Current odometer reading in kilometers.
        branch_id (str): ID of the branch where vehicle is located.
        status (VehicleStatus): Vehicle status (default: available).
    """

    plate_number: str = Field(
        ...,
        min_length=5,
        max_length=15,
        description="Vehicle license plate number",
    )
    brand: str = Field(..., min_length=2, max_length=50, description="Vehicle brand")
    model: str = Field(..., min_length=1, max_length=50, description="Vehicle model")
    year: int = Field(..., ge=1900, le=2030, description="Manufacturing year")
    vehicle_class: VehicleClassType = Field(..., description="Vehicle class category")
    price_per_day: float = Field(..., gt=0, description="Daily rental rate in dollars")
    mileage: float = Field(..., ge=0, description="Current odometer reading (km)")
    branch_id: str = Field(..., description="Branch ID where vehicle is located")
    status: VehicleStatus = Field(
        default=VehicleStatus.AVAILABLE,
        description="Vehicle status",
    )

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Validate manufacturing year is not in the future."""
        current_year = date.today().year
        if v > current_year:
            raise ValueError(f"Year cannot be in the future (max: {current_year})")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "plate_number": "34ABC123",
                "brand": "Toyota",
                "model": "Corolla",
                "year": 2023,
                "vehicle_class": "economy",
                "price_per_day": 45.0,
                "mileage": 15000.0,
                "branch_id": "branch-istanbul-1",
                "status": "available",
            }
        }
    }


class UpdateVehicleRequest(BaseModel):
    """
    Request body for updating vehicle information.

    Used by endpoint:
        - PUT /api/v1/vehicles/{vehicle_id}

    Attributes:
        brand (Optional[str]): Vehicle brand.
        model (Optional[str]): Vehicle model.
        vehicle_class (Optional[str]): Class category.
        price_per_day (Optional[float]): Daily rental rate.
        mileage (Optional[float]): Current odometer reading.
        branch_id (Optional[str]): Branch location.
        status (Optional[VehicleStatus]): Vehicle status.
    """

    brand: Optional[str] = Field(None, min_length=2, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=50)
    vehicle_class: Optional[VehicleClassType] = None
    price_per_day: Optional[float] = Field(None, gt=0)
    mileage: Optional[float] = Field(None, ge=0)
    branch_id: Optional[str] = None
    status: Optional[VehicleStatus] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "price_per_day": 50.0,
                "mileage": 16000.0,
                "status": "maintenance",
            }
        }
    }


class VehicleFilterRequest(BaseModel):
    """
    Query parameters for filtering vehicles.

    Used by endpoint: GET /api/v1/vehicles

    All fields are optional filters.

    Attributes:
        vehicle_class (Optional[str]): Filter by class.
        status (Optional[VehicleStatus]): Filter by status.
        branch_id (Optional[str]): Filter by branch.
        min_price (Optional[float]): Minimum price per day.
        max_price (Optional[float]): Maximum price per day.
        available_from (Optional[date]): Check availability from date.
        available_to (Optional[date]): Check availability until date.
    """

    vehicle_class: Optional[VehicleClassType] = Field(
        None, description="Filter by class"
    )
    status: Optional[VehicleStatus] = Field(None, description="Filter by status")
    branch_id: Optional[str] = Field(None, description="Filter by branch")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    available_from: Optional[date] = Field(None, description="Available from date")
    available_to: Optional[date] = Field(None, description="Available until date")

    @field_validator("max_price")
    @classmethod
    def validate_price_range(cls, v: Optional[float], info) -> Optional[float]:
        """Ensure max_price >= min_price if both provided."""
        if v is not None and info.data.get("min_price") is not None:
            if v < info.data["min_price"]:
                raise ValueError("max_price must be >= min_price")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "vehicle_class": "economy",
                "status": "available",
                "branch_id": "branch-istanbul-1",
                "min_price": 30.0,
                "max_price": 60.0,
            }
        }
    }
