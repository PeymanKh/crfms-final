"""
Request schemas for payment endpoints.

Author: Peyman Khodabandehlouei
Date: 06-01-2026
"""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


class CreditCardPaymentDetails(BaseModel):
    """Credit card payment details."""

    card_number: str = Field(
        ..., min_length=13, max_length=19, description="Credit card number"
    )
    cvv: str = Field(..., min_length=3, max_length=4, description="Card CVV")
    expiry: str = Field(
        ..., pattern=r"^\d{2}/\d{2}$", description="Card expiry (MM/YY)"
    )

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """Ensure card number contains only digits."""
        if not v.isdigit():
            raise ValueError("card_number must contain only digits")
        return v

    @field_validator("cvv")
    @classmethod
    def validate_cvv(cls, v: str) -> str:
        """Ensure CVV contains only digits."""
        if not v.isdigit():
            raise ValueError("cvv must contain only digits")
        return v


class PayPalPaymentDetails(BaseModel):
    """PayPal payment details."""

    email: str = Field(..., description="PayPal account email")
    auth_token: str = Field(
        ..., min_length=10, description="PayPal authentication token"
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation."""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v


class ProcessPaymentRequest(BaseModel):
    """Request body for processing payment."""

    reservation_id: str = Field(..., description="Reservation ID to pay for")
    payment_method: Literal["credit_card", "paypal"] = Field(
        ..., description="Payment method type"
    )

    credit_card_details: CreditCardPaymentDetails | None = Field(
        None, description="Credit card details (required if payment_method=credit_card)"
    )
    paypal_details: PayPalPaymentDetails | None = Field(
        None, description="PayPal details (required if payment_method=paypal)"
    )

    @field_validator("credit_card_details")
    @classmethod
    def validate_credit_card_details(cls, v, info):
        """Ensure credit card details provided when payment_method is credit_card."""
        payment_method = info.data.get("payment_method")
        if payment_method == "credit_card" and v is None:
            raise ValueError(
                "credit_card_details required when payment_method is 'credit_card'"
            )
        if payment_method != "credit_card" and v is not None:
            raise ValueError(
                "credit_card_details should only be provided when payment_method is 'credit_card'"
            )
        return v

    @field_validator("paypal_details")
    @classmethod
    def validate_paypal_details(cls, v, info):
        """Ensure PayPal details provided when payment_method is paypal."""
        payment_method = info.data.get("payment_method")
        if payment_method == "paypal" and v is None:
            raise ValueError("paypal_details required when payment_method is 'paypal'")
        if payment_method != "paypal" and v is not None:
            raise ValueError(
                "paypal_details should only be provided when payment_method is 'paypal'"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "reservation_id": "reservation-uuid-123",
                    "payment_method": "credit_card",
                    "credit_card_details": {
                        "card_number": "4532015112830366",
                        "cvv": "123",
                        "expiry": "12/26",
                    },
                },
                {
                    "reservation_id": "reservation-uuid-123",
                    "payment_method": "paypal",
                    "paypal_details": {
                        "email": "user@example.com",
                        "auth_token": "paypal-token-abc123xyz",
                    },
                },
            ]
        }
    }
