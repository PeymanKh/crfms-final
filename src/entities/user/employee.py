"""
This module implements abstract Employee class which is blueprints for creating Agent and Manager.
This class is an abstract method and cannot directly initialize in the app.

Note: Since Branch has branch attribute, inner class Branch import is used to avoid circular import issue.

Author: Peyman Khodabandehlouei
Date: 30-10-2025
"""

from datetime import date
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from entities.user import BaseUser
from schemas.entities import Gender, EmploymentType

if TYPE_CHECKING:
    from entities.branch import Branch


class Employee(BaseUser, ABC):
    """
    Abstract base class representing an employee in the application.

    This class is abstract and is not directly initialized, it provides common attributes for an employee.

    Args:
        first_name (str): First name of the employee.
        last_name (str): Last name of the employee.
        gender (Gender): Gender of the employee (Gender enum).
        birth_date (date): Birth date of the employee (must be >= 18 years ago).
        email (EmailStr): Email address of the employee.
        address (str): Home address of the employee.
        phone_number (str): Phone number of the employee.
        branch (Branch): Branch of the employee.
        is_active (bool): Whether the employee is active or not.
        salary (float): Salary of the employee.
        hire_date (date): Hire date of the employee.
        employment_type (EmploymentType): Employment type of the employee (EmploymentType enum).
        user_id (Optional[str]): ID of the employee.
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
        branch: "Branch",
        is_active: bool,
        salary: float,
        hire_date: date,
        employment_type: EmploymentType,
        user_id: Optional[str] = None,
    ) -> None:
        """Constructor method for Employee class."""
        # Call parent class constructor
        super().__init__(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            birth_date=birth_date,
            email=email,
            address=address,
            phone_number=phone_number,
            user_id=user_id,
        )

        # Validate branch
        from entities.branch import Branch  # To avoid circular import

        if not isinstance(branch, Branch):
            raise ValueError("Branch must be an instance of Branch class.")

        # Validate is_active
        if not isinstance(is_active, bool):
            raise ValueError("Is active must be a boolean value.")

        # Validate salary
        if not isinstance(salary, (int, float)):
            raise ValueError("Salary must be a numeric value.")
        if salary < 0:
            raise ValueError("Salary cannot be negative.")

        # Validate hire_date
        if not isinstance(hire_date, date):
            raise ValueError("Hire date must be a date object.")
        if hire_date > date.today():
            raise ValueError("Hire date cannot be in the future.")

        # Validate employment_type
        if not isinstance(employment_type, EmploymentType):
            raise ValueError("Employment type must be a valid EmploymentType enum.")

        # Assign values
        self.__branch = branch
        self.__is_active = is_active
        self.__salary = salary
        self.__hire_date = hire_date
        self.__employment_type = employment_type

        # Add employee to the branch
        branch.add_employee(self)

    @property
    def branch(self) -> "Branch":
        """Getter method for branch property."""
        return self.__branch

    @branch.setter
    def branch(self, new_branch: "Branch") -> None:
        """Setter method for branch property."""
        # Validation
        from entities.branch import Branch  # To avoid circular import

        if not isinstance(new_branch, Branch):
            raise ValueError("Branch must be an instance of Branch class.")

        self.__branch = new_branch

    @property
    def is_active(self) -> bool:
        """Getter method for is_active property."""
        return self.__is_active

    @is_active.setter
    def is_active(self, new_value):
        """Setter method for is_active property."""
        if not isinstance(new_value, bool):
            raise ValueError("Is active must be a boolean value.")

        self.__is_active = new_value

    @property
    def salary(self) -> float:
        """Getter method for salary property."""
        return self.__salary

    @salary.setter
    def salary(self, new_value):
        """Setter method for salary property."""
        if not isinstance(new_value, (int, float)):
            raise ValueError("Salary must be a numeric value.")
        if new_value < 0:
            raise ValueError("Salary cannot be negative.")

        self.__salary = new_value

    @property
    def hire_date(self) -> date:
        """Getter method for hire_date property."""
        return self.__hire_date

    @hire_date.setter
    def hire_date(self, new_value):
        """Setter method for hire_date property."""
        if not isinstance(new_value, date):
            raise ValueError("Hire date must be a date object.")
        if new_value > date.today():
            raise ValueError("Hire date cannot be in the future.")

        self.__hire_date = new_value

    @property
    def employment_type(self) -> EmploymentType:
        """Getter method for employment_type property."""
        return self.__employment_type.value

    @employment_type.setter
    def employment_type(self, new_value):
        """Setter method for employment_type property."""
        if not isinstance(new_value, EmploymentType):
            raise ValueError("Employment type must be a valid EmploymentType enum.")

        self.__employment_type = new_value

    @abstractmethod
    def get_work_schedule(self) -> float:
        """
        Return work schedule details including hours and shift patterns.
        Schedules differ by employment type and role.
        """
        pass
