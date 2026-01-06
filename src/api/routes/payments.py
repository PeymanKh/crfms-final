"""
Payment Routes

Handles HTTP endpoints for payment processing.

Author: Peyman Khodabandehlouei
Date: 06-01-2026
"""

import logging
from fastapi import APIRouter, status, HTTPException

from services import payment_service
from schemas.api import SuccessResponseWithPayload, ErrorResponse
from schemas.api.requests import ProcessPaymentRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])


@router.post(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Process payment for reservation",
    responses={
        200: {
            "description": "Payment processed successfully",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Validation error (reservation not found, invoice already paid)",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def process_payment(
    request: ProcessPaymentRequest,
) -> SuccessResponseWithPayload:
    """
    Process payment for a reservation.

    Business Flow:
        1. Validates reservation exists
        2. Checks invoice is in 'pending' status
        3. Processes payment using appropriate payment gateway (Factory pattern)
        4. Updates invoice status to 'completed' or 'failed'
        5. Returns receipt
    """
    try:
        # Call service layer
        payment_data = await payment_service.process_payment(request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message=f"Payment {payment_data.status}",
            data=payment_data.model_dump(),
        )

    except ValueError as e:
        # Business logic errors
        logger.warning(f"Payment validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Validation Error",
                "details": [
                    {
                        "field": None,
                        "message": str(e),
                        "error_code": "VALIDATION_ERROR",
                    }
                ],
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error during payment processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while processing payment",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )
