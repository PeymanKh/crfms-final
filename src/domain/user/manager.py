"""
This module implements Manager class.
It is a concrete class and can directly initialize in the app.

Author: Peyman Khodabandehlouei
Date: 07-11-2025
"""

from datetime import date
from typing import Any, TYPE_CHECKING, Optional

from domain.user import Employee
from schemas.domain import Gender, EmploymentType

if TYPE_CHECKING:
    from domain.branch import Branch
    from domain.vehicle import Vehicle, MaintenanceRecord


class Manager(Employee):
    """
    Concrete class representing a Manager in the application.

    Args:
        first_name (str): First name of the manager.
        last_name (str): Last name of the manager.
        gender (Gender): Gender of the manager.
        birth_date (date): Birth date of the manager (must be >= 18 years ago).
        email (str): Email address of the manager.
        address (str): Home address of the manager.
        phone_number (str): Phone number of the manager.
        branch (Branch): Branch where the manager works.
        is_active (bool): Whether the manager is active.
        salary (float): Salary of the manager.
        hire_date (date): Hire date of the manager.
        employment_type (EmploymentType): Employment type (full-time, part-time, contract).
        user_id (Optional[str]): ID of the manager.
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
            branch=branch,
            is_active=is_active,
            salary=salary,
            hire_date=hire_date,
            employment_type=employment_type,
            user_id=user_id,
        )

    @staticmethod
    def get_vehicle_information(vehicle: "Vehicle") -> dict[str, Any]:
        """
        Returns information of a vehicle

        Args:
            vehicle (Vehicle): Vehicle object

        Returns:
            dict[str, Any]: Dictionary containing vehicle information

        Raises:
            TypeError: If vehicle is not a Vehicle object
        """
        # Validate
        from domain.vehicle import Vehicle

        if not isinstance(vehicle, Vehicle):
            raise TypeError("vehicle must be a Vehicle object")

        return {
            "vehicle_id": vehicle.id,
            "vehicle_type": vehicle.vehicle_class.name,
            "vehicle_status": vehicle.status,
            "vehicle_brand": vehicle.brand,
            "vehicle_model": vehicle.model,
            "vehicle_color": vehicle.color,
            "vehicle_licence_plate": vehicle.licence_plate,
            "vehicle_fuel_level": vehicle.fuel_level,
            "vehicle_odometer": vehicle.odometer,
            "vehicle_last_service_odometer": vehicle.last_service_odometer,
            "vehicle_price_per_day": vehicle.price_per_day,
            "vehicle_maintenance_records": vehicle.maintenance_records,
        }

    @staticmethod
    def approve_maintenance(maintenance_record: "MaintenanceRecord") -> None:
        """
        Approves the maintenance request created by an agent

        Args:
            maintenance_record (MaintenanceRecord): maintenance record to approve

        Raises:
            TypeError: If maintenance_record is not a MaintenanceRecord object
        """
        # Validate
        from domain.vehicle import MaintenanceRecord

        if not isinstance(maintenance_record, MaintenanceRecord):
            raise TypeError("maintenance_record must be a MaintenanceRecord object")

        # Approve the maintenance request
        maintenance_record.vehicle.move_to_maintenance()

    def get_role(self) -> str:
        """Returns role of the user in the application"""
        return "manager"

    def get_information(self) -> dict[str, Any]:
        """Returns a dictionary including all user information"""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "birth_date": self.birth_date,
            "email": self.email,
            "phone_number": self.phone_number,
            "address": self.address,
            "branch": self.branch.id,
            "is_active": self.is_active,
            "salary": self.salary,
            "hire_date": self.hire_date,
            "employment_type": self.employment_type,
        }

    def get_work_schedule(self) -> dict[str, str]:
        """
        Return work schedule details including hours and shift patterns.
        Schedules differ by employment type and role.
        """
        if self.employment_type == EmploymentType.FULL_TIME:
            return {
                "hours_per_week": "40",
                "monday": "09:00-17:00",
                "tuesday": "09:00-17:00",
                "wednesday": "09:00-17:00",
                "thursday": "09:00-17:00",
                "friday": "09:00-17:00",
                "saturday": "off",
                "sunday": "off",
            }
        elif self.employment_type == EmploymentType.PART_TIME:
            return {
                "hours_per_week": "20",
                "monday": "09:00-13:00",
                "tuesday": "off",
                "wednesday": "09:00-13:00",
                "thursday": "off",
                "friday": "09:00-13:00",
                "saturday": "10:00-15:00",
                "sunday": "off",
            }
        else:
            return {
                "hours_per_week": "40",
                "monday": "10:00-18:00",
                "tuesday": "10:00-18:00",
                "wednesday": "10:00-18:00",
                "thursday": "10:00-18:00",
                "friday": "10:00-18:00",
                "saturday": "off",
                "sunday": "off",
            }

    def __str__(self):
        """Returns a string representation of the manager"""
        return f"Employee(Role: {self.get_role().title()}, Name: {self.first_name.title()} {self.last_name.title()}, Gender: {self.gender.title()}, Branch: {self.branch.id})"
