"""
Request schemas for authentication and user registration endpoints.

This module contains Pydantic models for user registration requests
including customers, agents, and managers.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import date
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict

from schemas.domain import Gender, EmploymentType


class CustomerRegistrationRequest(BaseModel):
    """
    Request body for customer registration.

    Business Rules:
        - User must be at least 18 years old
        - Email must be valid format
        - All fields are required

    Attributes:
        first_name (str): Customer's first name.
        last_name (str): Customer's last name.
        gender (Gender): Customer's gender (enum: male/female).
        birth_date (date): Customer's birth date (must be 18+ years old).
        email (EmailStr): Customer's email address.
        phone_number (str): Customer's phone number.
        address (str): Customer's home address.
        password (str): Account password (min 8 characters).
    """

    first_name: str = Field(
        ..., min_length=1, max_length=50, description="Customer's first name"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=50, description="Customer's last name"
    )
    gender: Gender = Field(..., description="Customer's gender")
    birth_date: date = Field(
        ..., description="Customer's birth date (must be at least 18 years old)"
    )
    email: EmailStr = Field(..., description="Customer's email address")
    phone_number: str = Field(
        ..., min_length=9, max_length=15, description="Customer's phone number"
    )
    address: str = Field(
        ..., min_length=1, max_length=200, description="Customer's home address"
    )
    password: str = Field(
        ..., min_length=8, description="Account password (minimum 8 characters)"
    )

    @field_validator("birth_date")
    @classmethod
    def validate_age(cls, value: date) -> date:
        """
        Validate that user is at least 18 years old.

        Args:
            value (date): Birth date to validate.

        Returns:
            date: Validated birth date.

        Raises:
            ValueError: If user is under 18 years old, or birth date is in the future.
        """
        today = date.today()
        eighteen_years_ago = today.replace(year=today.year - 18)

        if value > today:
            raise ValueError("Birth date cannot be in the future")

        if value > eighteen_years_ago:
            raise ValueError("User must be at least 18 years old")

        return value

    @field_validator("first_name", "last_name", "address")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """
        Validate that string fields are not empty or whitespace-only.

        Args:
            value (str): String value to validate.

        Returns:
            str: Validated string.

        Raises:
            ValueError: If string is empty or contains only whitespace.
        """
        if not value or value.strip() == "":
            raise ValueError("Field cannot be empty or contain only whitespace")

        return value.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Peyman",
                "last_name": "Khodabandehlouei",
                "gender": "male",
                "birth_date": "1999-03-15",
                "email": "peymankh@gmail.com",
                "phone_number": "+905343940796",
                "address": "123 Beşiktaş, Istanbul, Turkey",
                "password": "SecurePass123",
            }
        }
    )


class AgentRegistrationRequest(BaseModel):
    """
    Request body for agent registration.

    Note: This endpoint should be admin-only in production.

    Business Rules:
        - User must be at least 18 years old
        - An employment type is required for agents
        - Salary must be positive

    Attributes:
        first_name (str): Agent's first name.
        last_name (str): Agent's last name.
        gender (Gender): Agent's gender (enum: male/female).
        birth_date (date): Agent's birth date (must be 18+ years old).
        email (EmailStr): Agent's email address.
        phone_number (str): Agent's phone number.
        address (str): Agent's home address.
        password (str): Account password (min 8 characters).
        employment_type (EmploymentType): Employment type (full_time/part_time/contract).
        salary (float): Agent's salary (must be positive).
        branch_id (str): ID of the branch where agent works.
    """

    first_name: str = Field(
        ..., min_length=1, max_length=50, description="Agent's first name"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=50, description="Agent's last name"
    )
    gender: Gender = Field(..., description="Agent's gender")
    birth_date: date = Field(
        ..., description="Agent's birth date (must be at least 18 years old)"
    )
    email: EmailStr = Field(..., description="Agent's email address")
    phone_number: str = Field(
        ..., min_length=9, max_length=15, description="Agent's phone number"
    )
    address: str = Field(
        ..., min_length=1, max_length=200, description="Agent's home address"
    )
    password: str = Field(
        ..., min_length=8, description="Account password (minimum 8 characters)"
    )
    employment_type: EmploymentType = Field(..., description="Employment type")
    salary: float = Field(..., gt=0, description="Agent's salary (must be positive)")
    branch_id: str = Field(..., description="Branch ID where agent works")

    @field_validator("birth_date")
    @classmethod
    def validate_age(cls, value: date) -> date:
        """
        Validate that user is at least 18 years old.

        Args:
            value (date): Birth date to validate.

        Returns:
            date: Validated birth date.

        Raises:
            ValueError: If user is under 18 years old, or birth date is in the future.
        """
        today = date.today()
        eighteen_years_ago = today.replace(year=today.year - 18)

        if value > today:
            raise ValueError("Birth date cannot be in the future")

        if value > eighteen_years_ago:
            raise ValueError("User must be at least 18 years old")

        return value

    @field_validator("first_name", "last_name", "address")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """
        Validate that string fields are not empty or whitespace-only.

        Args:
            value (str): String value to validate.

        Returns:
            str: Validated string.

        Raises:
            ValueError: If string is empty or contains only whitespace.
        """
        if not value or value.strip() == "":
            raise ValueError("Field cannot be empty or contain only whitespace")

        return value.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Sarah",
                "last_name": "Azizi",
                "gender": "female",
                "birth_date": "1990-07-20",
                "email": "sarah.azizi@crfms.com",
                "phone_number": "+905559876543",
                "address": "456 Office Blvd, Istanbul, Turkey",
                "password": "AgentPass456",
                "employment_type": "full_time",
                "salary": 45000.0,
                "branch_id": "branch-123-abc",
            }
        }
    )


class ManagerRegistrationRequest(BaseModel):
    """
    Request body for manager registration.

    Note: This endpoint should be admin-only in production.

    Business Rules:
        - User must be at least 18 years old
        - An employment type is required for managers
        - Salary must be positive
        - Managers have additional responsibilities

    Attributes:
        first_name (str): Manager's first name.
        last_name (str): Manager's last name.
        gender (Gender): Manager's gender (enum: male/female).
        birth_date (date): Manager's birth date (must be 18+ years old).
        email (EmailStr): Manager's email address.
        phone_number (str): Manager's phone number.
        address (str): Manager's home address.
        password (str): Account password (min 8 characters).
        employment_type (EmploymentType): Employment type (full_time/part_time/contract).
        salary (float): Manager's salary (must be positive).
        branch_id (str): ID of the branch where manager works.
    """

    first_name: str = Field(
        ..., min_length=1, max_length=50, description="Manager's first name"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=50, description="Manager's last name"
    )
    gender: Gender = Field(..., description="Manager's gender")
    birth_date: date = Field(
        ..., description="Manager's birth date (must be at least 18 years old)"
    )
    email: EmailStr = Field(..., description="Manager's email address")
    phone_number: str = Field(
        ..., min_length=9, max_length=15, description="Manager's phone number"
    )
    address: str = Field(
        ..., min_length=1, max_length=200, description="Manager's home address"
    )
    password: str = Field(
        ..., min_length=8, description="Account password (minimum 8 characters)"
    )
    employment_type: EmploymentType = Field(..., description="Employment type")
    salary: float = Field(..., gt=0, description="Manager's salary (must be positive)")
    branch_id: str = Field(..., description="Branch ID where manager works")

    @field_validator("birth_date")
    @classmethod
    def validate_age(cls, value: date) -> date:
        """
        Validate that user is at least 18 years old.

        Args:
            value (date): Birth date to validate.

        Returns:
            date: Validated birth date.

        Raises:
            ValueError: If user is under 18 years old or birth date is in the future.
        """
        today = date.today()
        eighteen_years_ago = today.replace(year=today.year - 18)

        if value > today:
            raise ValueError("Birth date cannot be in the future")

        if value > eighteen_years_ago:
            raise ValueError("User must be at least 18 years old")

        return value

    @field_validator("first_name", "last_name", "address")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """
        Validate that string fields are not empty or whitespace-only.

        Args:
            value (str): String value to validate.

        Returns:
            str: Validated string.

        Raises:
            ValueError: If string is empty or contains only whitespace.
        """
        if not value or value.strip() == "":
            raise ValueError("Field cannot be empty or contain only whitespace")

        return value.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Ali",
                "last_name": "Talha",
                "gender": "male",
                "birth_date": "1985-11-10",
                "email": "ali.talha@crfms.com",
                "phone_number": "+905558765432",
                "address": "789 şişli, Istanbul, Turkey",
                "password": "ManagerPass789",
                "employment_type": "full_time",
                "salary": 75000.0,
                "branch_id": "branch-123-abc",
            }
        }
    )
