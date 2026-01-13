"""
Rental Routes

Handles HTTP endpoints for rental operations (pickup, return, extension, queries).

Author: Peyman Khodabandehlouei
Date: 13-01-2026
"""

import logging
from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Query

from services import rental_service
from schemas.api import SuccessResponseWithPayload, ErrorResponse
from schemas.api.requests.rentals import (
    PickupVehicleRequest,
    ReturnVehicleRequest,
    ExtendRentalRequest,
    RentalFilterRequest,
)

# Logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/rentals", tags=["Rentals"])


@router.post(
    "/pickup",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_201_CREATED,
    summary="Process vehicle pickup (idempotent)",
    responses={
        201: {
            "description": "Vehicle picked up successfully",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Business logic validation failed",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def pickup_vehicle(request: PickupVehicleRequest) -> SuccessResponseWithPayload:
    """
    Process vehicle pickup operation (creates rental from reservation).

    Business Flow:
        1. Validates reservation exists and is 'confirmed'
        2. Validates agent exists
        3. Checks vehicle is not maintenance-due
        4. Creates rental with initial odometer/fuel readings
        5. Updates reservation status to 'completed'

    Business Rules:
        - Reservation must be in 'confirmed' status
        - Vehicle must not be maintenance-due
        - pickup_token must be unique (enforced by database)
        - Odometer reading must be positive
        - Fuel level must be between 0.0 and 1.0

    """
    try:
        # Call service layer
        pickup_data = await rental_service.pickup_vehicle(request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message=pickup_data.message,
            data=pickup_data.rental.model_dump(),
        )

    except ValueError as e:
        # Business logic errors (reservation not found, wrong status, etc.)
        logger.warning(f"Validation error during vehicle pickup: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Validation Error",
                "details": [
                    {
                        "field": None,
                        "message": str(e),
                        "error_code": "PICKUP_VALIDATION_ERROR",
                    }
                ],
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error during vehicle pickup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred during vehicle pickup",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.post(
    "/{rental_id}/return",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Process vehicle return with charge calculation",
    responses={
        200: {
            "description": "Vehicle returned successfully with calculated charges",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Business logic validation failed",
            "model": ErrorResponse,
        },
        404: {
            "description": "Rental not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def return_vehicle(
    rental_id: str, request: ReturnVehicleRequest
) -> SuccessResponseWithPayload:
    """
    Process vehicle return operation with automatic charge calculation.

    Business Flow:
        1. Validates rental exists and is 'active'
        2. Validates agent exists
        3. Records return odometer/fuel readings
        4. Calculates all charges according to business rules
        5. Updates rental status to 'completed'

    """
    try:
        # Call service layer
        return_data = await rental_service.return_vehicle(rental_id, request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message=return_data.message,
            data=return_data.rental.model_dump(),
        )

    except ValueError as e:
        # Business logic errors
        logger.warning(f"Validation error during vehicle return: {e}")

        # Check if it's a "not found" error
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Rental Not Found",
                    "details": [
                        {
                            "field": "rental_id",
                            "message": str(e),
                            "error_code": "RENTAL_NOT_FOUND",
                        }
                    ],
                },
            )

        # Other validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Validation Error",
                "details": [
                    {
                        "field": None,
                        "message": str(e),
                        "error_code": "RETURN_VALIDATION_ERROR",
                    }
                ],
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error during vehicle return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred during vehicle return",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.post(
    "/{rental_id}/extend",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Extend rental return date",
    responses={
        200: {
            "description": "Rental extended successfully",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Business logic validation failed (conflict exists, invalid date)",
            "model": ErrorResponse,
        },
        404: {
            "description": "Rental not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def extend_rental(
    rental_id: str, request: ExtendRentalRequest
) -> SuccessResponseWithPayload:
    """
    Extend an active rental to a new return date.

    Business Flow:
        1. Validates rental exists and is 'active'
        2. Validates new_return_date is after current return_date
        3. Checks no conflicting reservation exists for the vehicle during extension period
        4. Updates reservation return_date
        5. Returns updated rental information

    Business Rules:
        - Rental must be in 'active' status (not completed)
        - new_return_date must be after current return_date
        - Vehicle must be available during extension period
        - Price recalculation for extended period
    """
    try:
        # Call service layer
        rental_data = await rental_service.extend_rental(rental_id, request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Rental extended successfully",
            data=rental_data.model_dump(),
        )

    except ValueError as e:
        # Business logic errors
        logger.warning(f"Validation error during rental extension: {e}")

        # Check if it's a "not found" error
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Rental Not Found",
                    "details": [
                        {
                            "field": "rental_id",
                            "message": str(e),
                            "error_code": "RENTAL_NOT_FOUND",
                        }
                    ],
                },
            )

        # Conflict or validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Validation Error",
                "details": [
                    {
                        "field": None,
                        "message": str(e),
                        "error_code": "EXTENSION_VALIDATION_ERROR",
                    }
                ],
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error during rental extension: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred during rental extension",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "/{rental_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Get rental by ID",
    responses={
        200: {
            "description": "Rental retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Rental not found",
            "model": ErrorResponse,
        },
    },
)
async def get_rental(rental_id: str) -> SuccessResponseWithPayload:
    """
    Get detailed information about a specific rental.

    Returns complete rental data including:
        - Rental status (active/completed)
        - Associated reservation, vehicle, customer, and agent IDs
        - Pickup readings (odometer, fuel, timestamp)
        - Return readings (if returned)
        - Itemized charges (if returned)
        - Creation and update timestamps

    """
    try:
        # Call service layer
        rental_data = await rental_service.get_rental_by_id(rental_id)

        if not rental_data:
            logger.info(f"Rental not found: {rental_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Rental Not Found",
                    "details": [
                        {
                            "field": "rental_id",
                            "message": f"Rental with ID '{rental_id}' does not exist",
                            "error_code": "RENTAL_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Rental retrieved successfully",
            data=rental_data.model_dump(),
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error retrieving rental {rental_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while retrieving rental",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="List rentals with optional filters",
    responses={
        200: {
            "description": "Rentals retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
    },
)
async def list_rentals(
    customer_id: Annotated[
        str | None, Query(description="Filter by customer ID")
    ] = None,
    vehicle_id: Annotated[str | None, Query(description="Filter by vehicle ID")] = None,
    agent_id: Annotated[str | None, Query(description="Filter by agent ID")] = None,
    status: Annotated[
        str | None, Query(description="Filter by status (active/completed)")
    ] = None,
    reservation_id: Annotated[
        str | None, Query(description="Filter by reservation ID")
    ] = None,
) -> SuccessResponseWithPayload:
    """
    List rentals with optional filters.

    All query parameters are optional. If no filters provided, returns all rentals.
    """
    try:
        # Build filter request
        filters = RentalFilterRequest(
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            agent_id=agent_id,
            status=status,
            reservation_id=reservation_id,
        )

        # Call service layer
        rental_list = await rental_service.list_rentals(filters)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message=f"Retrieved {rental_list.total_count} rentals",
            data=rental_list.model_dump(),
        )

    except Exception as e:
        logger.error(f"Unexpected error during rental listing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while listing rentals",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )
