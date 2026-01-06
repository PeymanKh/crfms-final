"""
Response schemas for reservation endpoints.

This module contains Pydantic models for reservation-related API responses.

Author: Peyman Khodabandehlouei
Date: 06-01-2026
"""

from datetime import datetime, date
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class ReservationAddOnData(BaseModel):
    """
    Add-on data in reservation responses.

    Attributes:
        id (str): Add-on unique identifier.
        name (str): Add-on name.
        price_per_day (float): Daily price.
    """

    id: str = Field(..., description="Add-on ID")
    name: str = Field(..., description="Add-on name")
    price_per_day: float = Field(..., description="Daily price")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "addon-uuid-123",
                "name": "GPS Navigation",
                "price_per_day": 5.0,
            }
        },
    )


class InvoiceData(BaseModel):
    """Invoice data embedded in reservation response."""

    id: str = Field(..., description="Invoice ID")
    status: str = Field(..., description="Invoice status (pending/completed/failed)")
    issued_date: date = Field(..., description="Invoice date")
    total_price: float = Field(..., description="Invoice total price")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "invoice-uuid-abc",
                "status": "pending",
                "issued_date": "2026-01-06",
                "total_price": 252.0,
            }
        },
    )


class ReservationData(BaseModel):
    """
    Reservation data payload for API responses.

    Used in:
        - POST /api/v1/reservations (create response)
        - GET /api/v1/reservations/{id} (get response)
        - PUT /api/v1/reservations/{id} (update response)
        - GET /api/v1/reservations (list of items)

    Attributes:
        id (str): Unique reservation identifier.
        status (str): Reservation status (pending/confirmed/cancelled/completed).
        customer_id (str): Customer who made the reservation.
        vehicle_id (str): Reserved vehicle ID.
        insurance_tier_id (str): Insurance tier ID.
        pickup_branch_id (str): Pickup branch ID.
        return_branch_id (str): Return branch ID.
        pickup_date (date): Pickup date.
        return_date (date): Return date.
        add_ons (List[ReservationAddOnData]): List of add-ons with details.
        total_price (float): Calculated total price (vehicle + insurance + add-ons).
        rental_days (int): Number of rental days.
        created_at (datetime): When reservation was created.
        updated_at (datetime): Last update timestamp.
    """

    id: str = Field(..., description="Reservation ID")
    status: str = Field(..., description="Reservation status")
    customer_id: str = Field(..., description="Customer ID")
    vehicle_id: str = Field(..., description="Vehicle ID")
    insurance_tier_id: str = Field(..., description="Insurance tier ID")
    pickup_branch_id: str = Field(..., description="Pickup branch ID")
    return_branch_id: str = Field(..., description="Return branch ID")
    pickup_date: date = Field(..., description="Pickup date")
    return_date: date = Field(..., description="Return date")
    add_ons: List[ReservationAddOnData] = Field(..., description="Add-ons list")
    total_price: float = Field(..., description="Total price")
    rental_days: int = Field(..., description="Number of rental days")
    invoice: InvoiceData = Field(..., description="Invoice information")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "reservation-uuid-123",
                "status": "pending",
                "customer_id": "customer-uuid-456",
                "vehicle_id": "vehicle-uuid-789",
                "insurance_tier_id": "tier-uuid-111",
                "pickup_branch_id": "branch-uuid-222",
                "return_branch_id": "branch-uuid-222",
                "pickup_date": "2026-02-01",
                "return_date": "2026-02-05",
                "add_ons": [
                    {
                        "id": "addon-uuid-1",
                        "name": "GPS Navigation",
                        "price_per_day": 5.0,
                    },
                    {
                        "id": "addon-uuid-2",
                        "name": "Child Seat",
                        "price_per_day": 3.0,
                    },
                ],
                "total_price": 252.0,
                "rental_days": 4,
                "invoice": {
                    "id": "invoice-uuid-abc",
                    "status": "pending",
                    "issued_date": "2026-01-06",
                    "total_price": 252.0,
                },
                "created_at": "2026-01-06T08:00:00Z",
                "updated_at": "2026-01-06T08:00:00Z",
            }
        },
    )


class ReservationListData(BaseModel):
    """
    Response data for reservation list endpoint.

    Used by: GET /api/v1/reservations

    Attributes:
        reservations (List[ReservationData]): List of reservations.
        total_count (int): Total number of reservations.
    """

    reservations: List[ReservationData] = Field(..., description="List of reservations")
    total_count: int = Field(..., description="Total reservations count")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reservations": [
                    {
                        "id": "reservation-uuid-123",
                        "status": "pending",
                        "customer_id": "customer-uuid-456",
                        "vehicle_id": "vehicle-uuid-789",
                        "insurance_tier_id": "tier-uuid-111",
                        "pickup_branch_id": "branch-uuid-222",
                        "return_branch_id": "branch-uuid-222",
                        "pickup_date": "2026-02-01",
                        "return_date": "2026-02-05",
                        "add_ons": [],
                        "total_price": 220.0,
                        "rental_days": 4,
                        "created_at": "2026-01-06T08:00:00Z",
                        "updated_at": "2026-01-06T08:00:00Z",
                    }
                ],
                "total_count": 1,
            }
        }
    )
