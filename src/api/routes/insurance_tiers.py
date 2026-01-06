"""
Insurance Tier Routes

Handles HTTP endpoints for insurance tier management (CRUD operations).

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

import logging
from fastapi import APIRouter, status, HTTPException

from services import insurance_tier_service
from schemas.api.common import SuccessResponseWithPayload, ErrorResponse
from schemas.api.requests import (
    CreateInsuranceTierRequest,
    UpdateInsuranceTierRequest,
)


# Logger
logger = logging.getLogger(__name__)


# Create router
router = APIRouter(prefix="/api/v1/insurance-tiers", tags=["Insurance Tiers"])


@router.post(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new insurance tier",
    responses={
        201: {
            "description": "Insurance tier created successfully",
            "model": SuccessResponseWithPayload,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def create_insurance_tier(
    request: CreateInsuranceTierRequest,
) -> SuccessResponseWithPayload:
    """
    Create a new insurance tier in the system.

    **Note:** In production, this endpoint should be restricted to manager users only.

    Insurance tiers define different levels of coverage customers can purchase
    (e.g., Basic, Standard, Premium).

    Business Rules:
        - Tier name must be at least 2 characters
        - Description must be at least 10 characters
        - Price per day must be non-negative
    """
    try:
        # Call service layer
        tier_data = await insurance_tier_service.create_insurance_tier(request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Insurance tier created successfully",
            data=tier_data.model_dump(),
        )

    except Exception as e:
        logger.error(f"Unexpected error during insurance tier creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while creating insurance tier",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="List all insurance tiers",
    responses={
        200: {
            "description": "Insurance tiers retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
    },
)
async def list_insurance_tiers() -> SuccessResponseWithPayload:
    """
    List all available insurance tiers in the system.

    Returns complete list of insurance tiers that customers can select
    when creating or modifying reservations.

    Each tier includes:
    - Tier name and coverage description
    - Daily insurance price
    - Creation and update timestamps
    """
    try:
        # Call service layer
        tier_list = await insurance_tier_service.list_insurance_tiers()

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message=f"Retrieved {tier_list.total_count} insurance tiers",
            data=tier_list.model_dump(),
        )

    except Exception as e:
        logger.error(f"Unexpected error during insurance tier listing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while listing insurance tiers",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "/{tier_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Get insurance tier by ID",
    responses={
        200: {
            "description": "Insurance tier retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Insurance tier not found",
            "model": ErrorResponse,
        },
    },
)
async def get_insurance_tier(tier_id: str) -> SuccessResponseWithPayload:
    """
    Get detailed information about a specific insurance tier.

    Returns complete tier data including:
    - Tier name and coverage description
    - Daily insurance price
    - Creation and update timestamps
    """
    try:
        # Call service layer
        tier_data = await insurance_tier_service.get_insurance_tier_by_id(tier_id)

        if not tier_data:
            logger.info(f"Insurance tier not found: {tier_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Insurance Tier Not Found",
                    "details": [
                        {
                            "field": "tier_id",
                            "message": f"Insurance tier with ID '{tier_id}' does not exist",
                            "error_code": "TIER_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Insurance tier retrieved successfully",
            data=tier_data.model_dump(),
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error retrieving insurance tier {tier_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while retrieving insurance tier",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.put(
    "/{tier_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Update insurance tier information",
    responses={
        200: {
            "description": "Insurance tier updated successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Insurance tier not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def update_insurance_tier(
    tier_id: str, request: UpdateInsuranceTierRequest
) -> SuccessResponseWithPayload:
    """
    Update insurance tier information.

    **Note:** In production, this endpoint should be restricted to manager users only.

    All fields are optional - only provided fields will be updated.
    Common updates:
    - Price adjustments
    - Coverage description improvements
    - Tier name changes
    """
    try:
        # Call service layer
        tier_data = await insurance_tier_service.update_insurance_tier(tier_id, request)

        if not tier_data:
            logger.info(f"Insurance tier not found for update: {tier_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Insurance Tier Not Found",
                    "details": [
                        {
                            "field": "tier_id",
                            "message": f"Insurance tier with ID '{tier_id}' does not exist",
                            "error_code": "TIER_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Insurance tier updated successfully",
            data=tier_data.model_dump(),
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error updating insurance tier {tier_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while updating insurance tier",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.delete(
    "/{tier_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Delete an insurance tier",
    responses={
        200: {
            "description": "Insurance tier deleted successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Insurance tier not found",
            "model": ErrorResponse,
        },
    },
)
async def delete_insurance_tier(tier_id: str) -> SuccessResponseWithPayload:
    """
    Delete an insurance tier from the system.

    **Note:** In production, this endpoint should be restricted to manager users only.

    **Warning:** This is a hard delete. Consider soft delete (is_available = false)
    for production to maintain historical data.

    **Important:** Before deleting a tier, ensure:
    - No active reservations are using this tier
    - Historical data integrity is maintained
    """
    try:
        # Call service layer
        success = await insurance_tier_service.delete_insurance_tier(tier_id)

        if not success:
            logger.info(f"Insurance tier not found for deletion: {tier_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Insurance Tier Not Found",
                    "details": [
                        {
                            "field": "tier_id",
                            "message": f"Insurance tier with ID '{tier_id}' does not exist",
                            "error_code": "TIER_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Insurance tier deleted successfully",
            data={"tier_id": tier_id},
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error deleting insurance tier {tier_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while deleting insurance tier",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )
