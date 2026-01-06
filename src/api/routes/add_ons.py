"""
Add-on Routes

Handles HTTP endpoints for add-on management (CRUD operations).

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

import logging
from fastapi import APIRouter, status, HTTPException

from services import add_on_service
from schemas.api.common import SuccessResponseWithPayload, ErrorResponse
from schemas.api.requests import (
    CreateAddOnRequest,
    UpdateAddOnRequest,
)


# Logger
logger = logging.getLogger(__name__)


# Create router
router = APIRouter(prefix="/api/v1/add-ons", tags=["Add-ons"])


@router.post(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new add-on",
    responses={
        201: {
            "description": "Add-on created successfully",
            "model": SuccessResponseWithPayload,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def create_add_on(request: CreateAddOnRequest) -> SuccessResponseWithPayload:
    """
    Create a new add-on in the system.

    **Note:** In production, this endpoint should be restricted to manager users only.

    Add-ons represent additional services customers can add to their reservations
    (e.g., GPS Navigation, Child Seat, Additional Driver).

    Business Rules:
        - Name must be at least 2 characters
        - Description must be at least 5 characters
        - Price per day must be non-negative
    """
    try:
        # Call service layer
        add_on_data = await add_on_service.create_add_on(request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Add-on created successfully",
            data=add_on_data.model_dump(),
        )

    except Exception as e:
        logger.error(f"Unexpected error during add-on creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while creating add-on",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="List all add-ons",
    responses={
        200: {
            "description": "Add-ons retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
    },
)
async def list_add_ons() -> SuccessResponseWithPayload:
    """
    List all available add-ons in the system.

    Returns complete list of add-ons that customers can select
    when creating or modifying reservations.

    Each add-on includes:
    - Name and description
    - Daily rental price
    - Creation and update timestamps
    """
    try:
        # Call service layer
        add_on_list = await add_on_service.list_add_ons()

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message=f"Retrieved {add_on_list.total_count} add-ons",
            data=add_on_list.model_dump(),
        )

    except Exception as e:
        logger.error(f"Unexpected error during add-on listing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while listing add-ons",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "/{add_on_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Get add-on by ID",
    responses={
        200: {
            "description": "Add-on retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Add-on not found",
            "model": ErrorResponse,
        },
    },
)
async def get_add_on(add_on_id: str) -> SuccessResponseWithPayload:
    """
    Get detailed information about a specific add-on.

    Returns complete add-on data including:
    - Name and description
    - Daily rental price
    - Creation and update timestamps
    """
    try:
        # Call service layer
        add_on_data = await add_on_service.get_add_on_by_id(add_on_id)

        if not add_on_data:
            logger.info(f"Add-on not found: {add_on_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Add-on Not Found",
                    "details": [
                        {
                            "field": "add_on_id",
                            "message": f"Add-on with ID '{add_on_id}' does not exist",
                            "error_code": "ADD_ON_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Add-on retrieved successfully",
            data=add_on_data.model_dump(),
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error retrieving add-on {add_on_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while retrieving add-on",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.put(
    "/{add_on_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Update add-on information",
    responses={
        200: {
            "description": "Add-on updated successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Add-on not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def update_add_on(
    add_on_id: str, request: UpdateAddOnRequest
) -> SuccessResponseWithPayload:
    """
    Update add-on information.

    **Note:** In production, this endpoint should be restricted to manager users only.

    All fields are optional - only provided fields will be updated.
    Common updates:
    - Price adjustments
    - Description improvements
    - Name corrections
    """
    try:
        # Call service layer
        add_on_data = await add_on_service.update_add_on(add_on_id, request)

        if not add_on_data:
            logger.info(f"Add-on not found for update: {add_on_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Add-on Not Found",
                    "details": [
                        {
                            "field": "add_on_id",
                            "message": f"Add-on with ID '{add_on_id}' does not exist",
                            "error_code": "ADD_ON_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Add-on updated successfully",
            data=add_on_data.model_dump(),
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error updating add-on {add_on_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while updating add-on",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.delete(
    "/{add_on_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Delete an add-on",
    responses={
        200: {
            "description": "Add-on deleted successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Add-on not found",
            "model": ErrorResponse,
        },
    },
)
async def delete_add_on(add_on_id: str) -> SuccessResponseWithPayload:
    """
    Delete an add-on from the system.

    **Note:** In production, this endpoint should be restricted to manager users only.

    **Warning:** This is a hard delete. Consider soft delete (is_available = false)
    for production to maintain historical data.

    **Important:** Before deleting an add-on, ensure:
    - No active reservations are using this add-on
    - Historical data integrity is maintained
    """
    try:
        # Call service layer
        success = await add_on_service.delete_add_on(add_on_id)

        if not success:
            logger.info(f"Add-on not found for deletion: {add_on_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Add-on Not Found",
                    "details": [
                        {
                            "field": "add_on_id",
                            "message": f"Add-on with ID '{add_on_id}' does not exist",
                            "error_code": "ADD_ON_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Add-on deleted successfully",
            data={"add_on_id": add_on_id},
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error deleting add-on {add_on_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while deleting add-on",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )
