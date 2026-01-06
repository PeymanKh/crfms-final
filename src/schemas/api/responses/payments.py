"""
Response schemas for payment endpoints.

Author: Peyman Khodabandehlouei
Date: 06-01-2026
"""

from pydantic import BaseModel, Field, ConfigDict


class PaymentData(BaseModel):
    """Payment processing result."""

    reservation_id: str = Field(..., description="Reservation ID")
    invoice_id: str = Field(..., description="Invoice ID")
    amount: float = Field(..., description="Payment amount")
    payment_method: str = Field(..., description="Payment method used")
    status: str = Field(..., description="Payment status (completed/failed)")
    receipt: str = Field(..., description="Payment receipt message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reservation_id": "reservation-uuid-123",
                "invoice_id": "invoice-uuid-456",
                "amount": 252.0,
                "payment_method": "credit_card",
                "status": "completed",
                "receipt": "Payment of $252.00 with card ending with 0366 was successful",
            }
        }
    )
