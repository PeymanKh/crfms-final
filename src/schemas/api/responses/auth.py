"""
Response schemas for authentication and user registration endpoints.

This module contains Pydantic models for user registration responses
including customers, agents, and managers.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class CustomerData(BaseModel):
    """
    Customer data payload for registration response.

    Used for:
        - POST /api/v1/auth/register (registration response)
        - GET /api/v1/customers/{id} (customer details query)

    Attributes:
        id (str): Unique customer identifier.
        first_name (str): Customer's first name.
        last_name (str): Customer's last name.
        gender (str): Customer's gender.
        birth_date (date): Customer's birth date.
        email (str): Customer's email address.
        phone_number (str): Customer's phone number.
        address (str): Customer's home address.
        role (str): User's role (always "customer").
        created_at (datetime): Account creation timestamp.
    """

    id: str = Field(..., description="Unique customer ID")
    first_name: str = Field(..., description="Customer's first name")
    last_name: str = Field(..., description="Customer's last name")
    gender: str = Field(..., description="Customer's gender")
    birth_date: date = Field(..., description="Customer's birth date")
    email: EmailStr = Field(..., description="Customer's email address")
    phone_number: str = Field(..., description="Customer's phone number")
    address: str = Field(..., description="Customer's home address")
    role: str = Field(..., description="User's role in the system")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "first_name": "Peyman",
                "last_name": "Khodabandehlouei",
                "gender": "male",
                "birth_date": "1999-03-15",
                "email": "peymankh@example.com",
                "phone_number": "+905551234567",
                "address": "123 Main St, Istanbul, Turkey",
                "role": "customer",
                "created_at": "2026-01-05T09:00:00Z",
            }
        },
    )


class EmployeeData(BaseModel):
    """
    Employee data payload for registration response.

    Used for:
        - POST /api/v1/users/agents (agent registration)
        - POST /api/v1/users/managers (manager registration)

    Attributes:
        id (str): Unique agent identifier.
        first_name (str): Agent's first name.
        last_name (str): Agent's last name.
        gender (str): Agent's gender.
        birth_date (date): Agent's birth date.
        email (str): Agent's email address.
        phone_number (str): Agent's phone number.
        address (str): Agent's home address.
        role (str): User's role (always "agent").
        employment_type (str): Employment type (full_time/part_time/contract).
        salary (float): Agent's salary.
        branch_id (str): ID of the branch where agent works.
        created_at (datetime): Account creation timestamp.
    """

    id: str = Field(..., description="Unique agent identifier")
    first_name: str = Field(..., description="Agent's first name")
    last_name: str = Field(..., description="Agent's last name")
    gender: str = Field(..., description="Agent's gender")
    birth_date: date = Field(..., description="Agent's birth date")
    email: EmailStr = Field(..., description="Agent's email address")
    phone_number: str = Field(..., description="Agent's phone number")
    address: str = Field(..., description="Agent's home address")
    role: str = Field(..., description="User's role in the system")
    employment_type: str = Field(..., description="Employment type")
    salary: float = Field(..., description="Agent's salary")
    branch_id: str = Field(..., description="Branch ID where agent works")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "660e9500-f39c-51e5-b827-557766551111",
                "first_name": "Sarah",
                "last_name": "Talha",
                "gender": "female",
                "birth_date": "1990-07-20",
                "email": "sarah.Talha@crfms.com",
                "phone_number": "+905559876543",
                "address": "456 Office Blvd, Istanbul, Turkey",
                "role": "agent",
                "employment_type": "full_time",
                "salary": 45000.0,
                "branch_id": "branch-123-abc",
                "created_at": "2026-01-05T09:00:00Z",
            }
        },
    )
