"""
Common Pydantic models and shared utilities for API schemas.

This module contains base models, error responses, and common validation
rules used across all API endpoints.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import timezone, datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class ErrorDetail(BaseModel):
    """Detailed error information."""

    field: Optional[str] = Field(None, description="Field name that caused the error.")
    message: str = Field(..., description="Error message.")
    error_code: Optional[str] = Field(None, description="Error code.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field": "pickup_date",
                "message": "Pickup date cannot be in the past",
                "error_code": "INVALID_DATE",
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response format"""

    success: bool = Field(False, description="Always False for error responses.")
    error: str = Field(..., description="Error message.")
    details: Optional[List[ErrorDetail]] = Field(
        None, description="Detailed error information."
    )
    timestamp: datetime = Field(
        default_factory=datetime.now(timezone.utc),
        description="Timestamp of the error.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "Validation Error",
                "details": [
                    {
                        "field": "vehicle_id",
                        "message": "Vehicle is not available",
                        "error_code": "VEHICLE_NOT_AVAILABLE",
                    }
                ],
                "timestamp": "2026-01-05T08:50:00Z",
            }
        }
    )


class SuccessResponse(BaseModel):
    """Standard success response format"""

    success: bool = Field(True, description="Always True for success responses.")
    message: str = Field(..., description="Success message.")
    timestamp: datetime = Field(
        default_factory=datetime.now(timezone.utc),
        description="Timestamp of the success.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Reservation approved successfully",
                "timestamp": "2026-01-05T08:50:00Z",
            }
        }
    )


class SuccessResponseWithPayload(BaseModel):
    """Standard success response format with data payload."""

    success: bool = Field(True, description="Always True for success responses.")
    message: str = Field(..., description="Success message.")
    data: Dict[str, Any] = Field(..., description="Response data payload.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the response.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Customer registered successfully",
                "data": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "first_name": "Peyman",
                    "last_name": "Khodabandehlouei",
                    "email": "peymankh@example.com",
                    "role": "customer",
                },
                "timestamp": "2026-01-05T10:30:00Z",
            }
        }
    )
