"""
Authentication Routes

Handles HTTP endpoints for user registration (customers, agents, managers).

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

import logging
from fastapi import APIRouter, status, HTTPException

from core.exceptions import DuplicateEmailError
from services.auth_service import auth_service
from schemas.api import ErrorResponse, SuccessResponseWithPayload
from schemas.api.requests import (
    CustomerRegistrationRequest,
    AgentRegistrationRequest,
    ManagerRegistrationRequest,
)

# Logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["Authentication (Registration Only)"])


@router.post(
    "/auth/register/customer",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer",
    responses={
        201: {
            "description": "Customer registered successfully",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Validation error or duplicate email",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def register_customer(
    request: CustomerRegistrationRequest,
) -> SuccessResponseWithPayload:
    """
    Register a new customer account.

    This endpoint creates a new Customer with the provided information.

    Business Rules:
        - Customer must be at least 18 years old
        - Email must be unique
        - Password must be at least 8 characters
    """
    try:
        # Call service layer
        customer_data = await auth_service.register_customer(request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Customer registered successfully",
            data=customer_data.model_dump(),
        )

    except DuplicateEmailError as e:
        logger.warning(f"Duplicate email registration attempt: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Duplicate Email",
                "details": [
                    {
                        "field": "email",
                        "message": str(e),
                        "error_code": "DUPLICATE_EMAIL",
                    }
                ],
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error during customer registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred during registration",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.post(
    "/auth/register/agent",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new agent",
    responses={
        201: {
            "description": "Agent registered successfully",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Validation error or duplicate email",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def register_agent(
    request: AgentRegistrationRequest,
) -> SuccessResponseWithPayload:
    """
    Register a new agent account.

    This endpoint creates a new Agent (Employee) with the provided information.

    Business Rules:
        - Agent must be at least 18 years old
        - Email must be unique
        - Salary must be positive
    """
    try:
        # Call service layer
        agent_data = await auth_service.register_agent(request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Agent registered successfully",
            data=agent_data.model_dump(),
        )

    except DuplicateEmailError as e:
        logger.warning(f"Duplicate email registration attempt: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Duplicate Email",
                "details": [
                    {
                        "field": "email",
                        "message": str(e),
                        "error_code": "DUPLICATE_EMAIL",
                    }
                ],
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error during agent registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred during registration",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.post(
    "/auth/register/manager",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new manager",
    responses={
        201: {
            "description": "Manager registered successfully",
            "model": SuccessResponseWithPayload,
        },
        400: {
            "description": "Validation error or duplicate email",
            "model": ErrorResponse,
        },
        422: {
            "description": "Request validation failed",
            "model": ErrorResponse,
        },
    },
)
async def register_manager(
    request: ManagerRegistrationRequest,
) -> SuccessResponseWithPayload:
    """
    Register a new manager account.

    This endpoint creates a new Manager (Employee) with the provided information.

    Business Rules:
        - Manager must be at least 18 years old
        - Email must be unique
        - Salary must be positive
    """
    try:
        # Call service layer
        manager_data = await auth_service.register_manager(request)

        # Return wrapped response
        return SuccessResponseWithPayload(
            success=True,
            message="Manager registered successfully",
            data=manager_data.model_dump(),
        )

    except DuplicateEmailError as e:
        logger.warning(f"Duplicate email registration attempt: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Duplicate Email",
                "details": [
                    {
                        "field": "email",
                        "message": str(e),
                        "error_code": "DUPLICATE_EMAIL",
                    }
                ],
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error during manager registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "details": [
                    {
                        "field": None,
                        "message": "An unexpected error occurred during registration",
                        "error_code": "INTERNAL_ERROR",
                    }
                ],
            },
        )


@router.get(
    "/auth/customers",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Get all customers",
)
async def get_all_customers() -> SuccessResponseWithPayload:
    """Get list of all registered customers."""
    customers = await auth_service.get_all_customers()
    return SuccessResponseWithPayload(
        success=True,
        message=f"Retrieved {len(customers)} customers",
        data={"customers": [c.model_dump() for c in customers]},
    )


@router.get(
    "/auth/employees",
    response_model=SuccessResponseWithPayload,
    status_code=status.HTTP_200_OK,
    summary="Get all employees (agents + managers)",
)
async def get_all_employees() -> SuccessResponseWithPayload:
    """Get list of all registered employees."""
    employees = await auth_service.get_all_employees()
    return SuccessResponseWithPayload(
        success=True,
        message=f"Retrieved {len(employees)} employees",
        data={"employees": [e.model_dump() for e in employees]},
    )
