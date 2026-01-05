"""
Vehicle Routes

Handles HTTP endpoints for vehicle management (CRUD operations).

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

import logging
from typing import Optional
from fastapi import APIRouter, status, HTTPException, Query
from pymongo.errors import DuplicateKeyError

from schemas.domain import VehicleStatus
from services.vehicle_service import vehicle_service
from schemas.api.common import SuccessResponseWithPayload, ErrorResponse
from schemas.api.requests import (
    CreateVehicleRequest,
    UpdateVehicleRequest,
    VehicleFilterRequest,
    VehicleClassType,
)


# Logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/vehicles", tags=["Vehicles"])


@router.post(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vehicle",
    responses={
        201: {
            "description": "Vehicle created successfully",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Validation error or duplicate plate number",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def create_vehicle(request: CreateVehicleRequest) -> SuccessResponseWithPayload:
    """
    Create a new vehicle in the system.

    Business Rules:
        - Plate number must be unique
        - Year cannot be in the future
        - Price must be greater than 0
        - Mileage must be non-negative
    """
    try:
        # Call service layer
        vehicle_data = await vehicle_service.create_vehicle(request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Vehicle created successfully",
            data=vehicle_data.model_dump(),
        )

    except DuplicateKeyError:
        logger.warning(f"Duplicate plate number attempt: {request.plate_number}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Duplicate Plate Number",
                "details": [
                    {
                        "field": "plate_number",
                        "message": f"Plate number '{request.plate_number}' already exists",
                        "error_code": "DUPLICATE_PLATE",
                    }
                ],
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error during vehicle creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while creating vehicle",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="List vehicles with optional filters",
    responses={
        200: {
            "description": "Vehicles retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
        422: {
            "description": "Invalid filter parameters",
            "model": ErrorResponse,
        },
    },
)
async def list_vehicles(
    vehicle_class: Optional[VehicleClassType] = Query(
        None, description="Filter by vehicle class"
    ),
    status_filter: Optional[VehicleStatus] = Query(
        None, alias="status", description="Filter by status"
    ),
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price per day"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price per day"),
) -> SuccessResponseWithPayload:
    """
    List all vehicles with optional filtering.

    Supports filtering by:
        - vehicle_class: economy, standard, luxury, suv
        - status: available, reserved, rented, maintenance
        - branch_id: Branch where vehicle is located
        - min_price: Minimum daily rental rate
        - max_price: Maximum daily rental rate
    """
    try:
        # Build filter request
        filters = VehicleFilterRequest(
            vehicle_class=vehicle_class,
            status=status_filter,
            branch_id=branch_id,
            min_price=min_price,
            max_price=max_price,
        )

        # Call service layer
        vehicle_list = await vehicle_service.list_vehicles(filters)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message=f"Retrieved {vehicle_list.total_count} vehicles",
            data=vehicle_list.model_dump(),
        )

    except Exception as e:
        logger.error(f"Unexpected error during vehicle listing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while listing vehicles",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "/{vehicle_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Get vehicle by ID",
    responses={
        200: {
            "description": "Vehicle retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Vehicle not found",
            "model": ErrorResponse,
        },
    },
)
async def get_vehicle(vehicle_id: str) -> SuccessResponseWithPayload:
    """
    Get detailed information about a specific vehicle.

    Returns complete vehicle data including:
        - Basic info (brand, model, year)
        - Pricing and availability
        - Current status and location
        - Maintenance history
    """
    try:
        # Call service layer
        vehicle_data = await vehicle_service.get_vehicle_by_id(vehicle_id)

        if not vehicle_data:
            logger.info(f"Vehicle not found: {vehicle_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Vehicle Not Found",
                    "details": [
                        {
                            "field": "vehicle_id",
                            "message": f"Vehicle with ID '{vehicle_id}' does not exist",
                            "error_code": "VEHICLE_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Vehicle retrieved successfully",
            data=vehicle_data.model_dump(),
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error retrieving vehicle {vehicle_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while retrieving vehicle",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.put(
    "/{vehicle_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Update vehicle information",
    responses={
        200: {
            "description": "Vehicle updated successfully",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Validation error or duplicate plate",
            "model": ErrorResponse,
        },
        404: {
            "description": "Vehicle not found",
            "model": ErrorResponse,
        },
    },
)
async def update_vehicle(
    vehicle_id: str, request: UpdateVehicleRequest
) -> SuccessResponseWithPayload:
    """
    Update vehicle information.

    **Note:** In production, this endpoint should be restricted to manager users only.

    All fields are optional - only provided fields will be updated.
    Common updates:
    - Mileage after maintenance
    - Status changes (available ↔ maintenance)
    - Price adjustments
    - Branch transfers
    """
    try:
        # Call service layer
        vehicle_data = await vehicle_service.update_vehicle(vehicle_id, request)

        if not vehicle_data:
            logger.info(f"Vehicle not found for update: {vehicle_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Vehicle Not Found",
                    "details": [
                        {
                            "field": "vehicle_id",
                            "message": f"Vehicle with ID '{vehicle_id}' does not exist",
                            "error_code": "VEHICLE_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Vehicle updated successfully",
            data=vehicle_data.model_dump(),
        )

    except DuplicateKeyError:
        logger.warning(f"Duplicate plate number in update for vehicle: {vehicle_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Duplicate Plate Number",
                "details": [
                    {
                        "field": "plate_number",
                        "message": "Plate number already exists",
                        "error_code": "DUPLICATE_PLATE",
                    }
                ],
            },
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error updating vehicle {vehicle_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while updating vehicle",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.delete(
    "/{vehicle_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Delete a vehicle",
    responses={
        200: {
            "description": "Vehicle deleted successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Vehicle not found",
            "model": ErrorResponse,
        },
    },
)
async def delete_vehicle(vehicle_id: str) -> SuccessResponseWithPayload:
    """Delete a vehicle from the system."""

    try:
        # Call service layer
        success = await vehicle_service.delete_vehicle(vehicle_id)

        if not success:
            logger.info(f"Vehicle not found for deletion: {vehicle_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Vehicle Not Found",
                    "details": [
                        {
                            "field": "vehicle_id",
                            "message": f"Vehicle with ID '{vehicle_id}' does not exist",
                            "error_code": "VEHICLE_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Vehicle deleted successfully",
            data={"vehicle_id": vehicle_id},
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error deleting vehicle {vehicle_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while deleting vehicle",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )
