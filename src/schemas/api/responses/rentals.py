"""
Rental API Response Schemas

Pydantic models for rental-related HTTP responses.
These models define the structure of data returned by rental endpoints.

Author: Peyman Khodabandehlouei
Date: 13-01-2026
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, computed_field


class RentalReadingData(BaseModel):
    """
    Response model for vehicle readings at pickup/return.

    Represents odometer and fuel level snapshot at a specific timestamp.
    """

    odometer: float = Field(..., description="Odometer reading in kilometers")
    fuel_level: float = Field(..., description="Fuel level (0.0 to 1.0)")
    timestamp: datetime = Field(..., description="When the reading was taken")

    class Config:
        json_schema_extra = {
            "example": {
                "odometer": 45000.5,
                "fuel_level": 1.0,
                "timestamp": "2026-01-13T14:30:00+03:00",
            }
        }


class RentalChargesData(BaseModel):
    """
    Response model for itemized rental charges.

    Calculated at return time with breakdown of all fees.

    Business Rules:
        - base_price: Original reservation total price
        - late_fee: $10/hour after 1-hour grace period
        - mileage_overage_fee: $0.50/km over 200km/day allowance
        - fuel_refill_fee: $50/full tank (proportional)
        - damage_fee: Manual assessment by agent
        - total: Sum of all charges
    """

    base_price: float = Field(..., description="Base reservation price")
    late_fee: float = Field(..., description="Late return fee")
    mileage_overage_fee: float = Field(..., description="Mileage overage charge")
    fuel_refill_fee: float = Field(..., description="Fuel refill charge")
    damage_fee: float = Field(..., description="Damage assessment")

    @computed_field
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

    class Config:
        json_schema_extra = {
            "example": {
                "base_price": 450.0,
                "late_fee": 30.0,
                "mileage_overage_fee": 25.0,
                "fuel_refill_fee": 12.5,
                "damage_fee": 150.0,
                "total": 667.5,
            }
        }


class RentalData(BaseModel):
    """
    Response model for rental details.

    Represents a complete rental record with all associated data.
    Returned by GET /api/v1/rentals/{rental_id} and pickup/return operations.
    """

    id: str = Field(..., description="Rental unique identifier")
    status: str = Field(..., description="Rental status (active/completed)")
    reservation_id: str = Field(..., description="Associated reservation ID")
    vehicle_id: str = Field(..., description="Assigned vehicle ID")
    customer_id: str = Field(..., description="Customer ID")
    agent_id: str = Field(..., description="Agent who processed pickup")
    pickup_token: str = Field(..., description="Idempotency token used at pickup")

    pickup_readings: RentalReadingData = Field(
        ..., description="Odometer/fuel at pickup"
    )
    return_readings: Optional[RentalReadingData] = Field(
        None, description="Odometer/fuel at return"
    )

    charges: Optional[RentalChargesData] = Field(
        None, description="Itemized charges (available after return)"
    )

    created_at: datetime = Field(
        ..., description="When rental was created (pickup time)"
    )
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rental-550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "reservation_id": "res-123abc",
                "vehicle_id": "vehicle-456def",
                "customer_id": "customer-789ghi",
                "agent_id": "agent-abc123",
                "pickup_token": "pickup-550e8400-1704892800",
                "pickup_readings": {
                    "odometer": 45000.5,
                    "fuel_level": 1.0,
                    "timestamp": "2026-01-13T14:30:00+03:00",
                },
                "return_readings": {
                    "odometer": 45850.2,
                    "fuel_level": 0.75,
                    "timestamp": "2026-01-15T16:45:00+03:00",
                },
                "charges": {
                    "base_price": 450.0,
                    "late_fee": 30.0,
                    "mileage_overage_fee": 25.0,
                    "fuel_refill_fee": 12.5,
                    "damage_fee": 150.0,
                    "total": 667.5,
                },
                "created_at": "2026-01-13T14:30:00+03:00",
                "updated_at": "2026-01-15T16:45:00+03:00",
            }
        }


class RentalListData(BaseModel):
    """
    Response model for rental list queries.

    Returned by GET /api/v1/rentals with optional filters.
    Contains array of rentals and total count.
    """

    rentals: List[RentalData] = Field(..., description="List of rental records")
    total_count: int = Field(
        ..., description="Total number of rentals matching filters"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rentals": [
                    {
                        "id": "rental-001",
                        "status": "active",
                        "reservation_id": "res-123",
                        "vehicle_id": "vehicle-456",
                        "customer_id": "customer-789",
                        "agent_id": "agent-abc",
                        "pickup_token": "pickup-001-1704892800",
                        "pickup_readings": {
                            "odometer": 45000.5,
                            "fuel_level": 1.0,
                            "timestamp": "2026-01-13T14:30:00+03:00",
                        },
                        "return_readings": None,
                        "charges": None,
                        "created_at": "2026-01-13T14:30:00+03:00",
                        "updated_at": "2026-01-13T14:30:00+03:00",
                    }
                ],
                "total_count": 1,
            }
        }


class PickupSuccessData(BaseModel):
    """
    Response model for successful vehicle pickup.

    Returned by POST /api/v1/rentals/pickup.
    Includes rental details and confirmation message.
    """

    rental: RentalData = Field(..., description="Created rental record")
    message: str = Field(
        default="Vehicle picked up successfully",
        description="Success confirmation message",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rental": {
                    "id": "rental-550e8400",
                    "status": "active",
                    "reservation_id": "res-123abc",
                    "vehicle_id": "vehicle-456def",
                    "customer_id": "customer-789ghi",
                    "agent_id": "agent-abc123",
                    "pickup_token": "pickup-550e8400-1704892800",
                    "pickup_readings": {
                        "odometer": 45000.5,
                        "fuel_level": 1.0,
                        "timestamp": "2026-01-13T14:30:00+03:00",
                    },
                    "return_readings": None,
                    "charges": None,
                    "created_at": "2026-01-13T14:30:00+03:00",
                    "updated_at": "2026-01-13T14:30:00+03:00",
                },
                "message": "Vehicle picked up successfully",
            }
        }


class ReturnSuccessData(BaseModel):
    """
    Response model for successful vehicle return.

    Returned by POST /api/v1/rentals/{rental_id}/return.
    Includes updated rental with calculated charges and summary.
    """

    rental: RentalData = Field(..., description="Completed rental record with charges")
    message: str = Field(
        default="Vehicle returned successfully",
        description="Success confirmation message",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rental": {
                    "id": "rental-550e8400",
                    "status": "completed",
                    "reservation_id": "res-123abc",
                    "vehicle_id": "vehicle-456def",
                    "customer_id": "customer-789ghi",
                    "agent_id": "agent-abc123",
                    "pickup_token": "pickup-550e8400-1704892800",
                    "pickup_readings": {
                        "odometer": 45000.5,
                        "fuel_level": 1.0,
                        "timestamp": "2026-01-13T14:30:00+03:00",
                    },
                    "return_readings": {
                        "odometer": 45850.2,
                        "fuel_level": 0.75,
                        "timestamp": "2026-01-15T16:45:00+03:00",
                    },
                    "charges": {
                        "base_price": 450.0,
                        "late_fee": 30.0,
                        "mileage_overage_fee": 25.0,
                        "fuel_refill_fee": 12.5,
                        "damage_fee": 150.0,
                        "total": 667.5,
                    },
                    "created_at": "2026-01-13T14:30:00+03:00",
                    "updated_at": "2026-01-15T16:45:00+03:00",
                },
                "message": "Vehicle returned successfully. Total charges: $667.50",
            }
        }
