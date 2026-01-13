"""
Rental API Request Schemas

Pydantic models for validating rental-related HTTP requests.
These models define the contract for rental operation endpoints.

Author: Peyman Khodabandehlouei
Date: 13-01-2026
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class PickupVehicleRequest(BaseModel):
    """
    Request model for vehicle pickup operation.

    This creates a new rental from an existing reservation.
    The pickup_token ensures idempotent pickup operations.

    Business Rules:
        - Reservation must exist and be in 'approved' status
        - Vehicle must not be maintenance-due
        - Agent must exist and be authorized
        - pickup_token must be unique (prevents duplicate pickups)
        - Odometer reading must be positive
        - Fuel level must be between 0 and 1 (0% to 100%)

    Example:
        {
            "reservation_id": "550e8400-e29b-41d4-a716-446655440000",
            "agent_id": "agent-123",
            "pickup_token": "pickup-550e8400-1234567890",
            "odometer_reading": 45000.5,
            "fuel_level": 1.0,
            "pickup_timestamp": "2026-01-13T14:30:00+03:00"
        }
    """

    reservation_id: str = Field(
        ..., min_length=1, description="Reservation ID to convert into rental"
    )

    agent_id: str = Field(..., min_length=1, description="Agent processing the pickup")

    pickup_token: str = Field(
        ...,
        min_length=1,
        description="Unique idempotency token (prevents duplicate pickups on retry)",
    )

    odometer_reading: float = Field(
        ..., gt=0, description="Current odometer reading in kilometers"
    )

    fuel_level: float = Field(
        ..., ge=0, le=1, description="Current fuel level (0.0 = empty, 1.0 = full tank)"
    )

    pickup_timestamp: Optional[datetime] = Field(
        None, description="Pickup timestamp (defaults to current time if not provided)"
    )

    @field_validator("odometer_reading")
    @classmethod
    def validate_odometer(cls, v: float) -> float:
        """Validate odometer reading is positive"""
        if v <= 0:
            raise ValueError("Odometer reading must be greater than 0")
        return v

    @field_validator("fuel_level")
    @classmethod
    def validate_fuel_level(cls, v: float) -> float:
        """Validate fuel level is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError("Fuel level must be between 0.0 (empty) and 1.0 (full)")
        return v

    @field_validator("pickup_token")
    @classmethod
    def validate_token_not_empty(cls, v: str) -> str:
        """Validate pickup token is not empty or whitespace"""
        if not v.strip():
            raise ValueError("pickup_token cannot be empty or whitespace")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "reservation_id": "550e8400-e29b-41d4-a716-446655440000",
                "agent_id": "agent-abc123",
                "pickup_token": "pickup-550e8400-1704892800",
                "odometer_reading": 45000.5,
                "fuel_level": 1.0,
                "pickup_timestamp": "2026-01-13T14:30:00+03:00",
            }
        }


class ReturnVehicleRequest(BaseModel):
    """
    Request model for vehicle return operation.

    Completes the rental by recording return readings and calculating charges.

    Business Rules:
        - Rental must exist and be in 'active' status
        - Agent must exist
        - Odometer reading must be >= pickup odometer
        - Fuel level must be between 0 and 1
        - Grace period: 1 hour free after due time
        - Late fee: $10/hour after grace period (rounded up)
        - Mileage allowance: 200 km/day
        - Mileage overage: $0.50/km over allowance
        - Fuel refill: $50/full tank (proportional if lower than pickup)
        - Damage charge: Optional manual assessment by agent

    Example:
        {
            "agent_id": "agent-123",
            "odometer_reading": 45850.2,
            "fuel_level": 0.75,
            "damage_charge": 150.0,
            "return_timestamp": "2026-01-15T16:45:00+03:00"
        }
    """

    agent_id: str = Field(..., min_length=1, description="Agent processing the return")

    odometer_reading: float = Field(
        ..., gt=0, description="Current odometer reading in kilometers at return"
    )

    fuel_level: float = Field(
        ...,
        ge=0,
        le=1,
        description="Current fuel level at return (0.0 = empty, 1.0 = full tank)",
    )

    damage_charge: Optional[float] = Field(
        default=0.0,
        ge=0,
        description="Manual damage assessment by agent (default: 0.0)",
    )

    return_timestamp: Optional[datetime] = Field(
        None, description="Return timestamp (defaults to current time if not provided)"
    )

    @field_validator("odometer_reading")
    @classmethod
    def validate_odometer(cls, v: float) -> float:
        """Validate odometer reading is positive"""
        if v <= 0:
            raise ValueError("Odometer reading must be greater than 0")
        return v

    @field_validator("fuel_level")
    @classmethod
    def validate_fuel_level(cls, v: float) -> float:
        """Validate fuel level is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError("Fuel level must be between 0.0 (empty) and 1.0 (full)")
        return v

    @field_validator("damage_charge")
    @classmethod
    def validate_damage_charge(cls, v: Optional[float]) -> float:
        """Validate damage charge is non-negative"""
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError("Damage charge cannot be negative")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent-abc123",
                "odometer_reading": 45850.2,
                "fuel_level": 0.75,
                "damage_charge": 150.0,
                "return_timestamp": "2026-01-15T16:45:00+03:00",
            }
        }


class ExtendRentalRequest(BaseModel):
    """
    Request model for extending an active rental.

    Allows customer to extend return date if no conflicts exist.

    Business Rules:
        - Rental must be in 'active' status
        - new_return_date must be after current return_date
        - Vehicle must not have conflicting reservation for extended period
        - Price recalculation based on extended days

    Example:
        {
            "new_return_date": "2026-01-20"
        }
    """

    new_return_date: date = Field(
        ..., description="New return date (must be after current return date)"
    )

    @field_validator("new_return_date")
    @classmethod
    def validate_future_date(cls, v: date) -> date:
        """Validate new return date is not in the past"""
        from datetime import date as date_type

        if v < date_type.today():
            raise ValueError("new_return_date cannot be in the past")
        return v

    class Config:
        json_schema_extra = {"example": {"new_return_date": "2026-01-20"}}


class RentalFilterRequest(BaseModel):
    """
    Request model for filtering rental list queries.

    All fields are optional - used as query parameters.

    Example query string:
        /api/v1/rentals?customer_id=abc123&status=active&agent_id=agent-xyz
    """

    customer_id: Optional[str] = Field(None, description="Filter by customer ID")

    vehicle_id: Optional[str] = Field(None, description="Filter by vehicle ID")

    agent_id: Optional[str] = Field(
        None, description="Filter by agent ID who processed pickup/return"
    )

    status: Optional[str] = Field(
        None, description="Filter by rental status (active/completed)"
    )

    reservation_id: Optional[str] = Field(
        None, description="Filter by associated reservation ID"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "customer-123",
                "status": "active",
                "agent_id": "agent-abc",
            }
        }
