"""
Request schemas for reservation endpoints.

This module contains Pydantic models for reservation-related API requests.

Author: Peyman Khodabandehlouei
Date: 06-01-2026
"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from schemas.domain import ReservationStatus


class CreateReservationRequest(BaseModel):
    """
    Request body for creating a new reservation.

    Used by endpoint:
        - POST /api/v1/reservations

    Attributes:
        customer_id (str): ID of the customer making the reservation.
        vehicle_id (str): ID of the vehicle to reserve.
        insurance_tier_id (str): ID of the insurance tier to use.
        pickup_branch_id (str): Branch ID for vehicle pickup.
        return_branch_id (str): Branch ID for vehicle return.
        pickup_date (date): Date when vehicle will be picked up.
        return_date (date): Date when vehicle will be returned.
        add_on_ids (List[str]): List of add-on IDs to include.
    """

    customer_id: str = Field(..., description="Customer ID")
    vehicle_id: str = Field(..., description="Vehicle ID")
    insurance_tier_id: str = Field(..., description="Insurance tier ID")
    pickup_branch_id: str = Field(..., description="Pickup branch ID")
    return_branch_id: str = Field(..., description="Return branch ID")
    pickup_date: date = Field(..., description="Pickup date (YYYY-MM-DD)")
    return_date: date = Field(..., description="Return date (YYYY-MM-DD)")
    add_on_ids: List[str] = Field(
        default_factory=list,
        description="List of add-on IDs",
    )

    @field_validator("return_date")
    @classmethod
    def validate_return_date(cls, v: date, info) -> date:
        """Ensure return_date is after pickup_date."""
        pickup_date = info.data.get("pickup_date")
        if pickup_date and v < pickup_date:
            raise ValueError("return_date must be after or equal to pickup_date")
        return v

    @field_validator("pickup_date")
    @classmethod
    def validate_pickup_date_not_past(cls, v: date) -> date:
        """Ensure pickup_date is not in the past."""
        from datetime import date as date_class

        today = date_class.today()
        if v < today:
            raise ValueError("pickup_date cannot be in the past")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "customer_id": "customer-uuid-123",
                "vehicle_id": "vehicle-uuid-456",
                "insurance_tier_id": "tier-uuid-789",
                "pickup_branch_id": "branch-uuid-111",
                "return_branch_id": "branch-uuid-111",
                "pickup_date": "2026-02-01",
                "return_date": "2026-02-05",
                "add_on_ids": ["addon-uuid-1", "addon-uuid-2"],
            }
        }
    }


class UpdateReservationRequest(BaseModel):
    """
    Request body for updating reservation information.

    Used by endpoint:
        - PUT /api/v1/reservations/{reservation_id}

    Attributes:
        status (Optional[ReservationStatus]): New reservation status.
        vehicle_id (Optional[str]): Change to different vehicle.
        insurance_tier_id (Optional[str]): Change insurance level.
        pickup_branch_id (Optional[str]): Change pickup location.
        return_branch_id (Optional[str]): Change return location.
        pickup_date (Optional[date]): Change pickup date.
        return_date (Optional[date]): Change return date.
        add_on_ids (Optional[List[str]]): Replace the add-ons list.
    """

    status: Optional[ReservationStatus] = None
    vehicle_id: Optional[str] = None
    insurance_tier_id: Optional[str] = None
    pickup_branch_id: Optional[str] = None
    return_branch_id: Optional[str] = None
    pickup_date: Optional[date] = None
    return_date: Optional[date] = None
    add_on_ids: Optional[List[str]] = None

    @field_validator("return_date")
    @classmethod
    def validate_return_date(cls, v: Optional[date], info) -> Optional[date]:
        """Ensure return_date is after pickup_date if both provided."""
        if v is None:
            return v
        pickup_date = info.data.get("pickup_date")
        if pickup_date and v < pickup_date:
            raise ValueError("return_date must be after or equal to pickup_date")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "approved",
                "return_date": "2026-02-07",
                "add_on_ids": ["addon-uuid-1"],
            }
        }
    }


class ReservationFilterRequest(BaseModel):
    """
    Query parameters for filtering reservations.

    Used by endpoint:
        - GET /api/v1/reservations

    Attributes:
        customer_id (Optional[str]): Filter by customer.
        vehicle_id (Optional[str]): Filter by vehicle.
        status (Optional[ReservationStatus]): Filter by status.
        pickup_date_from (Optional[date]): Filter pickups after this date.
        pickup_date_to (Optional[date]): Filter pickups before this date.
    """

    customer_id: Optional[str] = Field(None, description="Filter by customer")
    vehicle_id: Optional[str] = Field(None, description="Filter by vehicle")
    status: Optional[ReservationStatus] = Field(None, description="Filter by status")
    pickup_date_from: Optional[date] = Field(None, description="Pickup date from")
    pickup_date_to: Optional[date] = Field(None, description="Pickup date to")

    model_config = {
        "json_schema_extra": {
            "example": {
                "customer_id": "customer-uuid-123",
                "status": "pending",
                "pickup_date_from": "2026-02-01",
            }
        }
    }
