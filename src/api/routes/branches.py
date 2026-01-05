"""
Branch Routes

Handles HTTP endpoints for branch management (CRUD operations).

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

import logging
from fastapi import APIRouter, status, HTTPException

from services.branch_service import branch_service
from schemas.api import SuccessResponseWithPayload, ErrorResponse
from schemas.api.requests import CreateBranchRequest, UpdateBranchRequest


# Logger
logger = logging.getLogger(__name__)


# Create router
router = APIRouter(prefix="/api/v1/branches", tags=["Branches"])


@router.post(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new branch",
    responses={
        201: {
            "description": "Branch created successfully",
            "model": SuccessResponseWithPayload,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def create_branch(request: CreateBranchRequest) -> SuccessResponseWithPayload:
    """
    Create a new branch in the system.

    Business Rules:
        - Branch name must be at least 2 characters
        - City must be at least 2 characters
        - Phone number must be between 10-20 characters
    """
    try:
        # Call service layer
        branch_data = await branch_service.create_branch(request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Branch created successfully",
            data=branch_data.model_dump(),
        )

    except Exception as e:
        logger.error(f"Unexpected error during branch creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while creating branch",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="List all branches",
    responses={
        200: {
            "description": "Branches retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
    },
)
async def list_branches() -> SuccessResponseWithPayload:
    """
    List all branches in the system.

    Returns a complete list of branches with:
        - Basic info (name, city, address)
        - Contact details
        - Employee count
        - Timestamps
    """
    try:
        # Call service layer
        branch_list = await branch_service.list_branches()

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message=f"Retrieved {branch_list.total_count} branches",
            data=branch_list.model_dump(),
        )

    except Exception as e:
        logger.error(f"Unexpected error during branch listing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while listing branches",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "/{branch_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Get branch by ID",
    responses={
        200: {
            "description": "Branch retrieved successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Branch not found",
            "model": ErrorResponse,
        },
    },
)
async def get_branch(branch_id: str) -> SuccessResponseWithPayload:
    """
    Get detailed information about a specific branch.

    Returns complete branch data including:
        - Basic info (name, city, address)
        - Contact phone number
        - Number of employees working at this branch
        - Creation and update timestamps
    """
    try:
        # Call service layer
        branch_data = await branch_service.get_branch_by_id(branch_id)

        if not branch_data:
            logger.info(f"Branch not found: {branch_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Branch Not Found",
                    "details": [
                        {
                            "field": "branch_id",
                            "message": f"Branch with ID '{branch_id}' does not exist",
                            "error_code": "BRANCH_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Branch retrieved successfully",
            data=branch_data.model_dump(),
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error retrieving branch {branch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while retrieving branch",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.put(
    "/{branch_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Update branch information",
    responses={
        200: {
            "description": "Branch updated successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Branch not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def update_branch(
    branch_id: str, request: UpdateBranchRequest
) -> SuccessResponseWithPayload:
    """Update branch information."""

    try:
        # Call service layer
        branch_data = await branch_service.update_branch(branch_id, request)

        if not branch_data:
            logger.info(f"Branch not found for update: {branch_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Branch Not Found",
                    "details": [
                        {
                            "field": "branch_id",
                            "message": f"Branch with ID '{branch_id}' does not exist",
                            "error_code": "BRANCH_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Branch updated successfully",
            data=branch_data.model_dump(),
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error updating branch {branch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while updating branch",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.delete(
    "/{branch_id}",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Delete a branch",
    responses={
        200: {
            "description": "Branch deleted successfully",
            "model": SuccessResponseWithPayload,
        },
        404: {
            "description": "Branch not found",
            "model": ErrorResponse,
        },
    },
)
async def delete_branch(branch_id: str) -> SuccessResponseWithPayload:
    """Delete a branch from the system."""

    try:
        # Call service layer
        success = await branch_service.delete_branch(branch_id)

        if not success:
            logger.info(f"Branch not found for deletion: {branch_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Branch Not Found",
                    "details": [
                        {
                            "field": "branch_id",
                            "message": f"Branch with ID '{branch_id}' does not exist",
                            "error_code": "BRANCH_NOT_FOUND",
                        }
                    ],
                },
            )

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Branch deleted successfully",
            data={"branch_id": branch_id},
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions (404)

    except Exception as e:
        logger.error(f"Unexpected error deleting branch {branch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred while deleting branch",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )
