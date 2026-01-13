"""
Rental Database Models

Pydantic models for MongoDB rental documents with validation.
These models represent the database schema for rentals collection.

Author: Peyman Khodabandehlouei
Date: 13-01-2026
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RentalReadingDocument(BaseModel):
    """
    Embedded document for vehicle readings at pickup/return.

    Captures odometer and fuel level at a specific timestamp.
    """

    odometer: float = Field(..., ge=0, description="Odometer reading in kilometers")
    fuel_level: float = Field(
        ..., ge=0, le=1, description="Fuel level (0.0 to 1.0, where 1.0 = full tank)"
    )
    timestamp: datetime = Field(..., description="When the reading was taken")

    @field_validator("odometer")
    @classmethod
    def validate_odometer(cls, v: float) -> float:
        """Validate odometer is non-negative"""
        if v < 0:
            raise ValueError("Odometer reading cannot be negative")
        return v

    @field_validator("fuel_level")
    @classmethod
    def validate_fuel_level(cls, v: float) -> float:
        """Validate fuel level is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError("Fuel level must be between 0.0 and 1.0")
        return v


class RentalChargesDocument(BaseModel):
    """
    Embedded document for itemized rental charges calculated at return.

    Business Rules:
        - base_price: Original reservation total price
        - late_fee: $10/hour after 1-hour grace period
        - mileage_overage_fee: $0.50/km over 200km/day allowance
        - fuel_refill_fee: $50/full tank (proportional)
        - damage_fee: Manual assessment by agent
        - total: Sum of all charges
    """

    base_price: float = Field(..., ge=0, description="Base reservation price")
    late_fee: float = Field(
        default=0.0, ge=0, description="Late return fee ($10/hour after grace)"
    )
    mileage_overage_fee: float = Field(
        default=0.0,
        ge=0,
        description="Mileage overage charge ($0.50/km over allowance)",
    )
    fuel_refill_fee: float = Field(
        default=0.0, ge=0, description="Fuel refill charge ($50/full tank)"
    )
    damage_fee: float = Field(default=0.0, ge=0, description="Manual damage assessment")

    @property
    def total(self) -> float:
        """Calculate total charges (sum of all fees)"""
        return (
            self.base_price
            + self.late_fee
            + self.mileage_overage_fee
            + self.fuel_refill_fee
            + self.damage_fee
        )

    @field_validator(
        "base_price", "late_fee", "mileage_overage_fee", "fuel_refill_fee", "damage_fee"
    )
    @classmethod
    def validate_non_negative(cls, v: float) -> float:
        """Ensure all charges are non-negative"""
        if v < 0:
            raise ValueError("Charge amount cannot be negative")
        return v


class RentalDocument(BaseModel):
    """
    MongoDB document model for rentals collection.

    Represents an active vehicle rental created at pickup.
    Separate from Reservation - this tracks actual vehicle usage.

    Business Flow:
        1. Created at pickup with pickup_token (idempotency)
        2. Records initial odometer/fuel readings
        3. Status is 'active' until return
        4. At return: records return readings and calculates charges
        5. Status becomes 'completed' with finalized charges

    Indexes Required:
        - pickup_token (unique) - for idempotent pickup
        - reservation_id - for linking to reservation
        - agent_id - for agent query
        - status + created_at - for listing active rentals
    """

    id: str = Field(..., alias="_id", description="Rental unique identifier (UUID)")
    status: str = Field(..., description="Rental status (active/completed)")
    reservation_id: str = Field(..., description="Associated reservation ID")
    vehicle_id: str = Field(..., description="Assigned vehicle ID")
    customer_id: str = Field(..., description="Customer ID")
    agent_id: str = Field(..., description="Agent who processed pickup")
    pickup_token: str = Field(..., description="Unique token for idempotent pickup")

    pickup_readings: RentalReadingDocument = Field(
        ..., description="Odometer/fuel at pickup"
    )
    return_readings: Optional[RentalReadingDocument] = Field(
        None, description="Odometer/fuel at return"
    )

    charges: Optional[RentalChargesDocument] = Field(
        None, description="Itemized charges (calculated at return)"
    )

    created_at: datetime = Field(
        ..., description="When rental was created (pickup time)"
    )
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic model configuration"""

        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of allowed values"""
        allowed_statuses = ["active", "completed"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v

    @field_validator("pickup_token")
    @classmethod
    def validate_pickup_token(cls, v: str) -> str:
        """Validate pickup token is not empty"""
        if not v or not v.strip():
            raise ValueError("Pickup token cannot be empty")
        return v
