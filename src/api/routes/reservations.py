"""
Reservation Routes

Handles HTTP endpoints for reservation management (CRUD operations).

Author: Peyman Khodabandehlouei
Date: 06-01-2026
"""

import logging
from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Query

from services import reservation_service
from schemas.api import SuccessResponseWithPayload, ErrorResponse
from schemas.api.requests import (
    CreateReservationRequest,
    UpdateReservationRequest,
    ReservationFilterRequest,
)
from schemas.domain import ReservationStatus

# Logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/reservations", tags=["Reservations"])


@router.post(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reservation",
    responses={
        201: {
            "description": "Reservation created successfully",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Business logic validation failed (vehicle unavailable, entity not found)",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def create_reservation(
    request: CreateReservationRequest,
) -> SuccessResponseWithPayload:
    """
    Create a new reservation in the system.

    This endpoint handles the complete reservation flow:
    1. Validates all referenced entities (customer, vehicle, branches, insurance, add-ons)
    2. Checks vehicle availability for the requested dates
    3. Calculates price with appropriate discount strategy:
       - First reservation: 15% discount
       - Every 5th reservation: 10% loyalty discount
       - Others: No discount
    4. Creates reservation with 'pending' status

    **Price Calculation:**
    - Base: (vehicle_rate + insurance_rate + sum(addon_rates)) × rental_days
    - Discount applied based on customer's reservation history

    **Business Rules:**
    - Pickup date cannot be in the past
    - Return date must be after or equal to pickup date
    - Vehicle must be available for requested dates
    - All referenced entities must exist
    """
    try:
        # Call service layer
        reservation_data = await reservation_service.create_reservation(request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Reservation created successfully",
            data=reservation_data.model_dump(),
        )

    except ValueError as e:
        # Business logic errors (entity not found, vehicle unavailable)
        logger.warning(f"Validation error during reservation creation: {e}")
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
        logger.error(f"Unexpected error during reservation creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while creating reservation",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="List reservations with filters",
    responses={
        200: {
            "description": "Reservations retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
    },
)
async def list_reservations(
    customer_id: Annotated[
        str | None, Query(description="Filter by customer ID")
    ] = None,
    vehicle_id: Annotated[str | None, Query(description="Filter by vehicle ID")] = None,
    status_filter: Annotated[
        ReservationStatus | None,
        Query(alias="status", description="Filter by reservation status"),
    ] = None,
    pickup_date_from: Annotated[
        str | None, Query(description="Filter pickups from date (YYYY-MM-DD)")
    ] = None,
    pickup_date_to: Annotated[
        str | None, Query(description="Filter pickups to date (YYYY-MM-DD)")
    ] = None,
) -> SuccessResponseWithPayload:
    """
    List all reservations with optional filters.

    **Available Filters:**
    - `customer_id`: Get all reservations for a specific customer
    - `vehicle_id`: Get all reservations for a specific vehicle
    - `status`: Filter by reservation status (pending/confirmed/cancelled/completed)
    - `pickup_date_from`: Get reservations with pickup date >= this date
    - `pickup_date_to`: Get reservations with pickup date <= this date

    **Use Cases:**
    - Customer view: "My bookings" (filter by customer_id)
    - Vehicle schedule: "When is this car booked?" (filter by vehicle_id)
    - Admin dashboard: "All pending reservations" (filter by status)
    - Date range: "Bookings next week" (filter by date range)

    **Example Queries:**
    - `/reservations?customer_id=customer-123` - Customer's reservations
    - `/reservations?vehicle_id=vehicle-456&status=confirmed` - Confirmed bookings for a vehicle
    - `/reservations?pickup_date_from=2026-02-01&pickup_date_to=2026-02-07` - Week's reservations
    """
    try:
        # Build filter request
        from datetime import date as date_class

        filters = ReservationFilterRequest(
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            status=status_filter,
            pickup_date_from=(
                date_class.fromisoformat(pickup_date_from) if pickup_date_from else None
            ),
            pickup_date_to=(
                date_class.fromisoformat(pickup_date_to) if pickup_date_to else None
            ),
        )

        # Call service layer
        reservation_list = await reservation_service.list_reservations(filters)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message=f"Retrieved {reservation_list.total_count} reservations",
            data=reservation_list.model_dump(),
        )

    except ValueError as e:
        # Date parsing errors
        logger.warning(f"Invalid date format in filters: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Invalid Date Format",
                "details": [
                    {
                        "field": "pickup_date_from or pickup_date_to",
                        "message": "Date must be in YYYY-MM-DD format",
                        "error_code": "INVALID_DATE_FORMAT",
                    }
                ],
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error during reservation listing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while listing reservations",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "/{reservation_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Get reservation by ID",
    responses={
        200: {
            "description": "Reservation retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Reservation not found",
            "model": ErrorResponse,
        },
    },
)
async def get_reservation(reservation_id: str) -> SuccessResponseWithPayload:
    """
    Get detailed information about a specific reservation.

    Returns complete reservation data including:
    - All reference IDs (customer, vehicle, insurance, branches)
    - Expanded add-on details (name, price per day)
    - Calculated total price and rental days
    - Creation and update timestamps
    - Current status

    **Use Cases:**
    - View reservation details
    - Check booking confirmation
    - Verify pricing breakdown
    """
    try:
        # Call service layer
        reservation_data = await reservation_service.get_reservation_by_id(
            reservation_id
        )

        if not reservation_data:
            logger.info(f"Reservation not found: {reservation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Reservation Not Found",
                    "details": [
                        {
                            "field": "reservation_id",
                            "message": f"Reservation with ID '{reservation_id}' does not exist",
                            "error_code": "RESERVATION_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Reservation retrieved successfully",
            data=reservation_data.model_dump(),
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error retrieving reservation {reservation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while retrieving reservation",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.put(
    "/{reservation_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Update reservation information",
    responses={
        200: {
            "description": "Reservation updated successfully",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Business logic validation failed",
            "model": ErrorResponse,
        },
        404: {
            "description": "Reservation not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def update_reservation(
    reservation_id: str, request: UpdateReservationRequest
) -> SuccessResponseWithPayload:
    """
    Update reservation information.

    All fields are optional - only provided fields will be updated.

    **Business Rules:**
    - Cannot update reservations with status 'completed' or 'cancelled'
    - If vehicle changes, availability is checked automatically
    - If dates/vehicle/insurance/add-ons change, price is recalculated
    - Price recalculation uses customer's current reservation count for strategy

    **Price Recalculation Triggers:**
    - Vehicle changed
    - Insurance tier changed
    - Pickup or return date changed
    - Add-ons list changed

    **Common Updates:**
    - Change status: `{"status": "confirmed"}`
    - Extend rental: `{"return_date": "2026-02-10"}`
    - Add more add-ons: `{"add_on_ids": ["addon-1", "addon-2", "addon-3"]}`
    - Change vehicle: `{"vehicle_id": "vehicle-new-123"}`

    **Note:** Customer cannot be changed (business rule: reservation belongs to original customer)
    """
    try:
        # Call service layer
        reservation_data = await reservation_service.update_reservation(
            reservation_id, request
        )

        if not reservation_data:
            logger.info(f"Reservation not found for update: {reservation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Reservation Not Found",
                    "details": [
                        {
                            "field": "reservation_id",
                            "message": f"Reservation with ID '{reservation_id}' does not exist",
                            "error_code": "RESERVATION_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Reservation updated successfully",
            data=reservation_data.model_dump(),
        )

    except ValueError as e:
        # Business logic errors (status invalid, vehicle unavailable)
        logger.warning(f"Validation error during reservation update: {e}")
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

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error updating reservation {reservation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while updating reservation",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.delete(
    "/{reservation_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Delete a reservation",
    responses={
        200: {
            "description": "Reservation deleted successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Reservation not found",
            "model": ErrorResponse,
        },
    },
)
async def delete_reservation(reservation_id: str) -> SuccessResponseWithPayload:
    """
    Delete a reservation from the system.

    **⚠️ WARNING: This is a hard delete!**

    In production, consider:
    - Soft delete (set status to 'cancelled' instead)
    - Archive to separate collection for historical data
    - Implement business rules (e.g., cannot delete confirmed reservations)

    **Current Behavior:**
    - Permanently removes reservation from database
    - Cannot be undone
    - Historical data is lost

    **Recommended Alternative:**
    Use `PUT /reservations/{id}` with `{"status": "cancelled"}` instead for cancellations.
    """
    try:
        # Call service layer
        success = await reservation_service.delete_reservation(reservation_id)

        if not success:
            logger.info(f"Reservation not found for deletion: {reservation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Reservation Not Found",
                    "details": [
                        {
                            "field": "reservation_id",
                            "message": f"Reservation with ID '{reservation_id}' does not exist",
                            "error_code": "RESERVATION_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Reservation deleted successfully",
            data={"reservation_id": reservation_id},
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error deleting reservation {reservation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while deleting reservation",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )
