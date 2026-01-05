"""
MongoDB document schemas for auth service.

These models define the structure of documents stored in MongoDB collections.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


class CustomerDocument(BaseModel):
    """
    MongoDB document schema for the customers collection.

    Collection: customers

    Attributes:
        id (str): MongoDB document ID.
        first_name (str): Customer's first name.
        last_name (str): Customer's last name.
        gender (str): Customer's gender.
        birth_date (date): Customer's birth date.
        email (str): Customer's email address (indexed, unique).
        phone_number (str): Customer's phone number.
        address (str): Customer's home address.
        password_hash (str): Hashed password for authentication.
        role (str): Always "customer".
        created_at (datetime): Account creation timestamp.
        updated_at (Optional[datetime]): Last update timestamp.
    """

    id: str = Field(..., alias="_id", description="MongoDB document ID")
    first_name: str
    last_name: str
    gender: str
    birth_date: date
    email: str
    phone_number: str
    address: str
    password_hash: str
    role: str = "customer"
    created_at: datetime
    updated_at: Optional[datetime] = None


class EmployeeDocument(BaseModel):
    """
    MongoDB document schema for the employees collection.

    Collection: employees

    Attributes:
        id (str): MongoDB document ID.
        first_name (str): Employee's first name.
        last_name (str): Employee's last name.
        gender (str): Employee's gender.
        birth_date (date): Employee's birth date.
        email (str): Employee's email address (indexed, unique).
        phone_number (str): Employee's phone number.
        address (str): Employee's home address.
        password_hash (str): Hashed password for authentication.
        role (str): "agent" or "manager".
        employment_type (str): Employment type.
        salary (float): Employee's salary.
        branch_id (str): Branch where employee works.
        created_at (datetime): Account creation timestamp.
        updated_at (Optional[datetime]): Last update timestamp.
    """

    id: str = Field(..., alias="_id", description="MongoDB document ID")
    first_name: str
    last_name: str
    gender: str
    birth_date: date
    email: str
    phone_number: str
    address: str
    password_hash: str
    role: str
    employment_type: str
    salary: float
    branch_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "indexes": [
                {"keys": [("email", 1)], "unique": True},
                {"keys": [("branch_id", 1)]},
                {"keys": [("role", 1)]},
                {"keys": [("created_at", -1)]},
            ]
        },
    )
