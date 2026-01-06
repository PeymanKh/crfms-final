"""
Payment Service

Handles payment processing using Factory pattern for different payment methods.

Author: Peyman Khodabandehlouei
Date: 06-01-2026
"""

import logging

from core.database_manager import db_manager
from schemas.api.responses import PaymentData
from domain.payment import CreditCardPaymentCreator, PaypalPaymentCreator
from schemas.api.requests.payments import (
    ProcessPaymentRequest,
)

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for payment processing operations."""

    @staticmethod
    async def process_payment(request: ProcessPaymentRequest) -> PaymentData:
        """
        Process payment for a reservation using Factory pattern.

        Business Rules:
        1. Reservation must exist
        2. Invoice must be in 'pending' status
        3. Payment method is validated and processed
        4. Invoice status updated to 'completed' or 'failed'

        Args:
            request (ProcessPaymentRequest): Payment request with method details.

        Returns:
            PaymentData: Payment result with receipt.

        Raises:
            ValueError: If reservation not found or invoice already paid
        """
        # Validate reservation exists
        reservation_doc = await db_manager.find_reservation_by_id(
            request.reservation_id
        )
        if not reservation_doc:
            raise ValueError(
                f"Reservation with ID '{request.reservation_id}' not found"
            )

        # Check invoice status
        invoice = reservation_doc["invoice"]
        if invoice["status"] != "pending":
            raise ValueError(
                f"Invoice already processed with status: {invoice['status']}"
            )

        # Get payment amount from invoice
        amount = invoice["total_price"]

        # Create payment factory based on method

        payment_factory = PaymentService._create_payment_factory(request)
        # Execute payment using factory pattern
        receipt = payment_factory.execute_payment(amount)

        # Determine payment success (check if receipt contains "successful")
        payment_success = "successful" in receipt.lower()
        new_invoice_status = "completed" if payment_success else "failed"

        # Update invoice status in database
        await db_manager.update_reservation(
            request.reservation_id, {"invoice.status": new_invoice_status}
        )

        logger.info(
            f"Payment {new_invoice_status} for reservation {request.reservation_id}: "
            f"${amount} via {request.payment_method}"
        )

        # Return payment result
        return PaymentData(
            reservation_id=request.reservation_id,
            invoice_id=invoice["id"],
            amount=amount,
            payment_method=request.payment_method,
            status=new_invoice_status,
            receipt=receipt,
        )

    @staticmethod
    def _create_payment_factory(request: ProcessPaymentRequest):
        """Factory method to create appropriate payment factory."""

        if request.payment_method == "credit_card":
            if not request.credit_card_details:
                raise ValueError("Credit card details required")
            return CreditCardPaymentCreator(
                card_number=request.credit_card_details.card_number,
                cvv=request.credit_card_details.cvv,
                expiry=request.credit_card_details.expiry,
            )

        elif request.payment_method == "paypal":
            if not request.paypal_details:
                raise ValueError("PayPal details required")
            return PaypalPaymentCreator(
                email=request.paypal_details.email,
                auth_token=request.paypal_details.auth_token,
            )

        else:
            raise ValueError(f"Unsupported payment method: {request.payment_method}")


# Singleton instance
payment_service = PaymentService()
