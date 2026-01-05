"""
This module implements abstract BaseUser class which is blueprints for creating customers and employees.
This class is an abstract method and cannot directly initialize in the app.

Business Rules:
    - id is auto-generated
    - Users must be at least 18 years old
    - Gender and ID are immutable once set

Author: Peyman Khodabandehlouei
Date: 30-10-2025
"""

import uuid
from datetime import date
from abc import ABC, abstractmethod
from typing import Optional

from schemas.domain import Gender


class BaseUser(ABC):
    """
    Abstract base class representing a user in the application.
    This class is abstract and is not directly initialized, it provides common attributes for a person.

    Args:
        first_name (str): First name of the person.
        last_name (str): Last name of the person.
        gender (Gender): Gender of the person (Gender enum).
        birth_date (date): Birth date of the person (must be >= 18 years ago).
        email (EmailStr): Email address of the person.
        address (str): Home address of the person.
        phone_number (str): Phone number of the person.
        user_id: (Optional[str]) User id of the person.
    """

    def __init__(
        self,
        first_name: str,
        last_name: str,
        gender: Gender,
        birth_date: date,
        email: str,
        address: str,
        phone_number: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Constructor method for BaseUser class."""
        # Validate first_name
        if not isinstance(first_name, str):
            raise TypeError("First name must be a string.")
        if first_name == "":
            raise ValueError("First name cannot be empty.")

        # Validate last_name
        if not isinstance(last_name, str):
            raise TypeError("Last name must be a string.")
        if last_name == "":
            raise ValueError("Last name cannot be empty.")

        # Validate gender
        if not isinstance(gender, Gender):
            raise ValueError("Gender must be a valid Gender enum.")

        # Validate email
        if not isinstance(email, str):
            raise TypeError("Email must be a string.")
        if "@" not in email:
            raise ValueError("Email must be a valid email address.")

        # Validate birth_date
        if not isinstance(birth_date, date):
            raise ValueError("Birth date must be a valid date object.")
        eighteen_years_ago = date.today().replace(year=date.today().year - 18)
        if birth_date > eighteen_years_ago:
            raise ValueError("User must be at least 18 years old.")

        # Validate address
        if not isinstance(address, str):
            raise TypeError("Address must be a string.")
        if address == "":
            raise ValueError("Address cannot be empty.")

        # Validate phone_number
        if not isinstance(phone_number, str):
            raise TypeError("Phone number must be a string.")
        if phone_number == "":
            raise ValueError("Phone number cannot be empty.")

        # Validate id
        if user_id is not None and not isinstance(user_id, str):
            raise TypeError("user_id must be a string.")
        if user_id == "":
            raise ValueError("user_id cannot be empty.")

        self.__id = user_id if user_id is not None else str(uuid.uuid4())
        self.__first_name = first_name
        self.__last_name = last_name
        self.__gender = gender
        self.__birth_date = birth_date
        self.__email = email
        self.__address = address
        self.__phone_number = phone_number

    @property
    def id(self) -> str:
        """
        Getter method for id property.

        Note: ID is auto-generated and immutable. Cannot be modified after creation.
        """
        return self.__id

    @property
    def first_name(self) -> str:
        """Getter method for first_name property."""
        return self.__first_name

    @first_name.setter
    def first_name(self, new_value) -> None:
        """Setter method for first_name property."""
        # Validation
        if not isinstance(new_value, str):
            raise TypeError("First name must be a string.")
        if new_value == "":
            raise ValueError("First name cannot be empty.")

        # Business logic
        self.__first_name = new_value

    @property
    def last_name(self) -> str:
        """Getter method for last_name property."""
        return self.__last_name

    @last_name.setter
    def last_name(self, new_value) -> None:
        """Setter method for last_name property."""
        # Validation
        if not isinstance(new_value, str):
            raise TypeError("Last name must be a string.")
        if new_value == "":
            raise ValueError("Last name cannot be empty.")

        # Business logic
        self.__last_name = new_value

    @property
    def gender(self) -> Gender:
        """
        Getter method for gender property.

        Note: Gender is immutable once set during initialization.
        """
        return self.__gender.value

    @property
    def birth_date(self) -> date:
        """
        Getter for birth_date property (returns a date object).

        Note: Users must be at least 18 years old to register in the system.
        """
        return self.__birth_date

    def birth_date_str(self) -> str:
        """Returns the birth date as DD-MM-YYYY string."""
        return self.__birth_date.strftime("%d-%m-%Y")

    @birth_date.setter
    def birth_date(self, new_value) -> None:
        """
        Setter method for birth_date property

        Note: Users must be at least 18 years old to register in the system.
        """
        # Convert string to a date object if needed
        new_date = (
            date.fromisoformat(new_value) if isinstance(new_value, str) else new_value
        )
        eighteen_years_ago = date.today().replace(year=date.today().year - 18)

        # Validation
        if new_date > date.today():
            raise ValueError("Birth date cannot be in the future.")

        if new_date > eighteen_years_ago:
            raise ValueError("User must be at least 18 years old.")

        # Business logic
        self.__birth_date = new_date

    @property
    def email(self) -> str:
        """Getter method for email property."""
        return self.__email

    @email.setter
    def email(self, new_value) -> None:
        """Setter method for email property."""
        # Validation
        if not isinstance(new_value, str):
            raise TypeError("Email must be a string.")
        if "@" not in new_value:  # Basic sanity check
            raise ValueError("Email must be a valid email address.")

        # Business logic
        self.__email = new_value

    @property
    def address(self) -> str:
        """Getter method for address property."""
        return self.__address

    @address.setter
    def address(self, new_value) -> None:
        """Setter method for address property."""
        # Validation
        if not isinstance(new_value, str):
            raise TypeError("Address must be a string.")
        if new_value == "":
            raise ValueError("Address cannot be empty.")

        # Business logic
        self.__address = new_value

    @property
    def phone_number(self) -> str:
        """Getter method for phone_number property."""
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, new_value) -> None:
        """Setter method for phone_number property."""
        # Validation
        if not isinstance(new_value, str):
            raise TypeError("Phone number must be a string.")
        if new_value == "":
            raise ValueError("Phone number cannot be empty.")

        # Business logic
        self.__phone_number = new_value

    @abstractmethod
    def get_role(self) -> str:
        """Return the role of the user."""
        pass

    @abstractmethod
    def get_information(self) -> str:
        """Return information of the user"""
        pass
