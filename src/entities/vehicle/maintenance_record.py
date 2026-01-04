"""
This module implements MaintenanceRecord class.
This class is a concrete method and can directly initialize in the app.

Business logic:
    - id is automatically generated and can't be edited.
    - service_date is autogenerate from date of creating it.
    - odometer is autogenerate from Vehicle's current odometer and is immutable.

Author: Peyman Khodabandehlouei
Date: 30-10-2025
"""

import uuid
from datetime import date, datetime
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from core import ClockService
    from entities.vehicle import Vehicle


class MaintenanceRecord:
    """
    Concrete class representing a maintenance record in the application.

    Args:
        vehicle (Vehicle): Vehicle instance representing the maintenance record.
        note (Optional[str]): Optional note about the maintenance.
        record_id (Optional[str]): Explicit id (used e.g. for persistence).
        service_date (Optional[date]): Explicit service date; defaults to today.
        odometer (Optional[int | float]): Explicit odometer; defaults to vehicle.odometer.
        clock (Optional[ClockService]): Clock service for time-based calculations.
    Raises:
        TypeError: If vehicle is not a Vehicle instance, or note is not a string.
    """

    def __init__(
        self,
        vehicle: "Vehicle",
        note: Optional[str] = None,
        record_id: Optional[str] = None,
        service_date: Optional[date] = None,
        odometer: Optional[int] = None,
        clock: Optional["ClockService"] = None,
    ):
        from entities.vehicle import Vehicle  # avoid circular import

        # Validate vehicle
        if not isinstance(vehicle, Vehicle):
            raise TypeError("vehicle must be a Vehicle object")

        # Validate note
        if note is not None and not isinstance(note, str):
            raise TypeError("note must be a string object")

        # Validate id
        if record_id is not None and not isinstance(record_id, str):
            raise TypeError("record_id must be a string.")
        if record_id == "":
            raise ValueError("record_id cannot be empty.")

        # Validate service_date
        if service_date is not None and not isinstance(service_date, date):
            raise TypeError("service_date must be a date object.")

        # Validate odometer
        if odometer is not None and not isinstance(odometer, (int, float)):
            raise TypeError("odometer must be a number.")

        # Assign values
        # Add dynamic clock service
        from core import SystemClock

        self._clock = clock or SystemClock()

        self.__id = record_id if record_id is not None else str(uuid.uuid4())
        self.__vehicle = vehicle
        self.__service_date = (
            service_date if service_date is not None else self._clock.today()
        )
        self.__odometer = odometer if odometer is not None else self.__vehicle.odometer
        self.__note = note

    @property
    def id(self) -> str:
        """Getter for the id"""
        return self.__id

    @property
    def vehicle(self) -> "Vehicle":
        """Getter for the vehicle"""
        return self.__vehicle

    @vehicle.setter
    def vehicle(self, vehicle: "Vehicle") -> None:
        """
        Setter for the vehicle

        Args:
            vehicle (Vehicle): Vehicle instance of the record.

        Raises:
            TypeError: If vehicle is not a Vehicle instance.
        """
        # Validation
        from entities.vehicle import Vehicle  # To avoid circular import

        if not isinstance(vehicle, Vehicle):
            raise TypeError("vehicle must be a Vehicle object")

        # Logic
        self.__vehicle = vehicle

    @property
    def service_date(self) -> date:
        """Getter for the service date"""
        return self.__service_date

    @service_date.setter
    def service_date(self, service_date: date) -> None:
        """
        Setter for the service date

        Args:
            service_date (date): Service date of the record.

        Raises:
            TypeError: If service_date is a datetime object.
            TypeError: If service_date is not a date object.
            ValueError: If service_date is in future date.
        """
        # Validation
        if isinstance(service_date, datetime):
            raise TypeError("service_date must be a date object, not datetime")
        if not isinstance(service_date, date):
            raise TypeError("service_date must be a date object")
        if service_date > self._clock.today():
            raise ValueError("service_date can not be in the future")

        # Logic
        self.__service_date = service_date

    @property
    def odometer(self) -> float:
        """Getter for the odometer"""
        return self.__odometer

    @property
    def note(self) -> Optional[str]:
        """Getter for the note"""
        return self.__note

    @note.setter
    def note(self, note: Optional[str]) -> None:
        """
        Setter for the note

        Args:
            note (Optional[str]): Optional note about the maintenance.

        Raises:
            TypeError: If note is not a string object or None.
        """
        # Validation
        if note is not None and not isinstance(note, str):
            raise TypeError("Note must be a string object or None")

        # Logic
        self.__note = note
