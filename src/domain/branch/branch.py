"""
This module implements concrete Branch class.
This class is a concrete class and can directly initialize in the app.

Note: Since Branch has employees attribute, inner class Employee import is used to avoid circular import issue.

Author: Peyman Khodabandehlouei
Date: 30-10-2025
"""

import uuid
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.user import Employee


class Branch:
    """
    Concrete class representing a branch in the application.
    This class can be directly initialized and used during application runtime.

    Args:
        name (str): Name of the branch.
        city (str): City of the branch.
        address (str): Address of the branch.
        phone_number (str): Phone number of the branch.
        employees (Optional[List[Employee]]): List of employees working in the branch.
        branch_id (Optional[str]): ID of the branch.

    Raises:
        TypeError: If name is not a string.
        TypeError: If city is not a string.
        TypeError: If address is not a string.
        TypeError: If phone_number is not a string.
        TypeError: If employees is not a list.
        TypeError: If any employee is not an instance of Employee class.
    """

    def __init__(
        self,
        name: str,
        city: str,
        address: str,
        phone_number: str,
        employees: Optional[List["Employee"]] = None,
        branch_id: Optional[str] = None,
    ) -> None:
        """Constructor method for Branch class."""
        # Validate name
        if not isinstance(name, str):
            raise TypeError("name must be a string.")

        # Validate city
        if not isinstance(city, str):
            raise TypeError("city must be a string.")

        # Validate address
        if not isinstance(address, str):
            raise TypeError("address must be a string.")

        # Validate phone_number
        if not isinstance(phone_number, str):
            raise TypeError("phone_number must be a string.")

        # Validate employees
        if employees is None:
            employees = []

        # Validate employee is a list
        if not isinstance(employees, list):
            raise TypeError("employees must be a list.")
        # Validate all items in the list are Employee instances
        from domain.user import Employee  # To avoid circular import

        if not all(isinstance(employee, Employee) for employee in employees):
            raise TypeError("all employees must be instances of Employee class.")

        # Validate id
        if branch_id is not None and not isinstance(branch_id, str):
            raise TypeError("branch_id must be a string.")
        if branch_id == "":
            raise ValueError("branch_id cannot be empty.")

        # Assign values
        self.__id = branch_id if branch_id is not None else str(uuid.uuid4())
        self.__name = name
        self.__city = city
        self.__address = address
        self.__phone_number = phone_number
        self.__employees = employees.copy()

    @property
    def id(self) -> str:
        """
        Getter method for id property.

        Note: ID is auto-generated and immutable. Cannot be modified after creation.
        """
        return self.__id

    @property
    def name(self) -> str:
        """Getter method for name property."""
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        """
        Setter method for name property.

        Args:
            name (str): Name of the branch.

        Raises:
            TypeError: If name is not a string.
        """
        # Validation
        if not isinstance(name, str):
            raise TypeError("name must be a string.")

        # Business logic
        self.__name = name

    @property
    def city(self) -> str:
        """Getter method for city property."""
        return self.__city

    @city.setter
    def city(self, city: str) -> None:
        """
        Setter method for city property.

        Args:
            city (str): City of the branch.

        Raises:
            TypeError: If city is not a string.
        """
        # Validation
        if not isinstance(city, str):
            raise TypeError("city must be a string.")

        # Business logic
        self.__city = city

    @property
    def address(self) -> str:
        """Getter method for address property."""
        return self.__address

    @address.setter
    def address(self, address: str) -> None:
        """
        Setter method for address property

        Args:
            address (str): Address of the branch.

        Raises:
            TypeError: If address is not a string.
        """
        # Validation
        if not isinstance(address, str):
            raise TypeError("address must be a string.")

        # Business logic
        self.__address = address

    @property
    def phone_number(self) -> str:
        """Getter method for phone_number property."""
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, phone_number: str) -> None:
        """
        Setter method for phone_number property

        Args:
            phone_number (str): New phone number of the branch.

        Raises:
            TypeError: If phone_number is not a string.
        """
        # Validation
        if not isinstance(phone_number, str):
            raise TypeError("phone_number must be a string.")

        # Business logic
        self.__phone_number = phone_number

    @property
    def employees(self) -> List["Employee"]:
        """Getter method for employees"""
        return self.__employees.copy()

    @employees.setter
    def employees(self, new_employees: List["Employee"]) -> None:
        """
        Setter method for employees property.

        Args:
            new_employees (List[Employee]): A list of Employee instances.

        Raises:
            TypeError: If new_employees is not a list or if employees items are not instances of Employee.
        """
        # Validation
        if not isinstance(new_employees, list):
            raise TypeError("employees must be a list.")

        from domain.user import Employee  # To avoid circular import

        if not all(isinstance(emp, Employee) for emp in new_employees):
            raise TypeError("All employees must be instances of Employee class.")

        # Business logic
        self.__employees = new_employees.copy()

    def has_employee(self, employee_id: str) -> bool:
        """
        Method to check if an employee is working in the branch.

        Args:
            employee_id (str): The unique ID of the employee to search for.

        Raises:
            TypeError: If employee_id is not a string.
            ValueError: If employee_id is empty.
        """
        # Validation
        if not isinstance(employee_id, str):
            raise TypeError("Employee ID must be a string.")
        if not employee_id:  # Now specifically for empty string
            raise ValueError("Employee ID cannot be empty.")

        # Logic
        return any(emp.id == employee_id for emp in self.__employees)

    def add_employee(self, employee: "Employee") -> None:
        """
        Method to add a new employee to the branch.

        Args:
            employee (Employee): The employee to add.

        Raises:
            TypeError: If employee is not an instance of Employee.
            ValueError: If employee already exists in the employees list.
        """
        # Validate employee is an instance of Employee class
        from domain.user import Employee  # To avoid circular import

        if not isinstance(employee, Employee):
            raise TypeError("Employee must be an instance of Employee class.")

        # Validate if employee is not already working in the branch
        if any(emp.id == employee.id for emp in self.__employees):
            raise ValueError("Employee is already working in the branch.")

        self.__employees.append(employee)

    def remove_employee(self, employee_id: str) -> None:
        """
        Method to remove an employee from the branch.

        Args:
            employee_id (str): The unique ID of the employee to remove.

        Raises:
            TypeError: If employee_id is not a string.
            ValueError: employee is not found in the employees list.
        """
        # Validate employee_id is a string
        if not isinstance(employee_id, str):
            raise TypeError("Employee ID must be a string.")

        # Check if employee exists in the branch
        if not self.has_employee(employee_id):
            raise ValueError("Employee with the given ID is not found.")

        self.__employees = [emp for emp in self.__employees if emp.id != employee_id]

    def __str__(self):
        """String representation of the Branch object."""
        return f"Branch(id={self.__id}, name={self.__name}, city={self.__city}, address={self.__address}, phone_number={self.__phone_number}, employees={self.__employees})"
