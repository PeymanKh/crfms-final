"""
Authentication Service

Handles user registration logic.
This module orchestrates domain entity creation and database persistence.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

import uuid
import logging
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

from core.database_manager import db_manager
from core.exceptions import DuplicateEmailError
from schemas.api.responses.auth import CustomerData, EmployeeData
from schemas.db_models import CustomerDocument, EmployeeDocument
from schemas.api.requests.auth import (
    CustomerRegistrationRequest,
    AgentRegistrationRequest,
    ManagerRegistrationRequest,
)


logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for authentication and user registration operations.

    Handles business logic for creating new users (customers, agents, managers)
    """

    @staticmethod
    async def register_customer(request: CustomerRegistrationRequest) -> CustomerData:
        """
        Register a new customer.

        Args:
            request (CustomerRegistrationRequest): Validated customer registration data.

        Returns:
            CustomerData: Created customer data for response.

        Raises:
            DuplicateEmailError: If email already exists in the database.
        """
        # Check if email already exists
        existing_customer = await db_manager.find_customer_by_email(request.email)
        if existing_customer:
            logger.warning(
                f"Registration attempt with duplicate email: {request.email}"
            )
            raise DuplicateEmailError(email=request.email)

        # Generate customer ID
        customer_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)

        # Create database document
        customer_doc = CustomerDocument(
            _id=customer_id,
            first_name=request.first_name,
            last_name=request.last_name,
            gender=request.gender.value,
            birth_date=request.birth_date,
            email=request.email,
            phone_number=request.phone_number,
            address=request.address,
            password_hash=request.password,
            role="customer",
            created_at=current_time,
            updated_at=current_time,
        )

        # Save to the database
        try:
            await db_manager.create_customer(customer_doc)
            logger.info(f"Successfully registered customer: {customer_id}")
        except DuplicateKeyError:
            logger.error(f"Duplicate key error for email: {request.email}")
            raise DuplicateEmailError(email=request.email)

        # Return response data
        return CustomerData(
            id=customer_id,
            first_name=request.first_name,
            last_name=request.last_name,
            gender=request.gender.value,
            birth_date=request.birth_date,
            email=request.email,
            phone_number=request.phone_number,
            address=request.address,
            role="customer",
            created_at=current_time,
        )

    @staticmethod
    async def register_agent(request: AgentRegistrationRequest) -> EmployeeData:
        """
        Register a new agent.

        Args:
            request (AgentRegistrationRequest): Validated agent registration data.

        Returns:
            EmployeeData: Created agent data for response.

        Raises:
            DuplicateEmailError: If email already exists in database.
        """
        # Check if email already exists
        existing_employee = await db_manager.find_employee_by_email(request.email)
        if existing_employee:
            logger.warning(
                f"Registration attempt with duplicate email: {request.email}"
            )
            raise DuplicateEmailError(email=request.email)

        # Generate agent ID
        agent_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)

        # Create database document
        employee_doc = EmployeeDocument(
            _id=agent_id,
            first_name=request.first_name,
            last_name=request.last_name,
            gender=request.gender.value,
            birth_date=request.birth_date,
            email=request.email,
            phone_number=request.phone_number,
            address=request.address,
            password_hash=request.password,
            role="agent",
            employment_type=request.employment_type.value,
            salary=request.salary,
            branch_id=request.branch_id,
            created_at=current_time,
        )

        # Save to the database
        try:
            await db_manager.create_employee(employee_doc)
            logger.info(f"Successfully registered agent: {agent_id}")
        except DuplicateKeyError:
            logger.error(f"Duplicate key error for email: {request.email}")
            raise DuplicateEmailError(email=request.email)

        # Return response data
        return EmployeeData(
            id=agent_id,
            first_name=request.first_name,
            last_name=request.last_name,
            gender=request.gender.value,
            birth_date=request.birth_date,
            email=request.email,
            phone_number=request.phone_number,
            address=request.address,
            role="agent",
            employment_type=request.employment_type.value,
            salary=request.salary,
            branch_id=request.branch_id,
            created_at=current_time,
        )

    @staticmethod
    async def register_manager(request: ManagerRegistrationRequest) -> EmployeeData:
        """
        Register a new manager.

        Args:
            request (ManagerRegistrationRequest): Validated manager registration data.

        Returns:
            EmployeeData: Created manager data for response.

        Raises:
            DuplicateEmailError: If email already exists in the database.
        """
        # Check if email already exists
        existing_employee = await db_manager.find_employee_by_email(request.email)
        if existing_employee:
            logger.warning(
                f"Registration attempt with duplicate email: {request.email}"
            )
            raise DuplicateEmailError(email=request.email)

        # Generate manager ID
        manager_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)

        # Create database document
        employee_doc = EmployeeDocument(
            _id=manager_id,
            first_name=request.first_name,
            last_name=request.last_name,
            gender=request.gender.value,
            birth_date=request.birth_date,
            email=request.email,
            phone_number=request.phone_number,
            address=request.address,
            password_hash=request.password,
            role="manager",
            employment_type=request.employment_type.value,
            salary=request.salary,
            branch_id=request.branch_id,
            created_at=current_time,
        )

        # Save to the database
        try:
            await db_manager.create_employee(employee_doc)
            logger.info(f"Successfully registered manager: {manager_id}")
        except DuplicateKeyError:
            logger.error(f"Duplicate key error for email: {request.email}")
            raise DuplicateEmailError(email=request.email)

        # Return response data
        return EmployeeData(
            id=manager_id,
            first_name=request.first_name,
            last_name=request.last_name,
            gender=request.gender.value,
            birth_date=request.birth_date,
            email=request.email,
            phone_number=request.phone_number,
            address=request.address,
            role="manager",
            employment_type=request.employment_type.value,
            salary=request.salary,
            branch_id=request.branch_id,
            created_at=current_time,
        )


# Singleton instance
auth_service = AuthService()
