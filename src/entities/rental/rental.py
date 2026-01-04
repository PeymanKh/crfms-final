"""
This module implements Rental class.
Rental represents active car usage, separate from reservation booking.

Business Logic:
    - Rental is created at pickup with odometer/fuel readings
    - Grace period: 1 hour after due time (no late fee)
    - Late fee: $10 per hour after grace period
    - Mileage allowance: 200 km per day
    - Mileage overage: $0.50 per km over allowance
    - Fuel refill: $50 per full tank (proportional)
    - pickup_token ensures idempotent pickup operations

Author: Peyman Khodabandehlouei
Date: 04-01-2026
"""

import uuid
import math
from datetime import timedelta
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core import ClockService
    from entities.reservation import Reservation
    from schemas.entities import RentalCharges, RentalReading

# Business rule constants
LATE_FEE_PER_HOUR = 10.0
DAILY_KM_ALLOWANCE = 200.0
OVERAGE_PER_KM = 0.5
FUEL_REFILL_RATE = 50.0


class Rental:
    """
    Concrete class representing an active rental (vehicle in use).

    This class is separate from Reservation - while Reservation represents
    the booking intent, Rental represents actual vehicle usage with real
    odometer/fuel readings and charge calculations.

    Args:
        reservation (Reservation): The associated reservation.
        pickup_token (str): Unique token for idempotent pickup operations.
        pickup_readings (RentalReading): Odometer/fuel readings at pickup.
        clock (ClockService): Clock service for time-based calculations.
        rental_id (Optional[str]): Explicit rental ID (used for persistence).

    Raises:
        TypeError: If any parameter has an incorrect type.
        ValueError: If readings or token are invalid.
    """

    def __init__(
        self,
        reservation: "Reservation",
        pickup_token: str,
        pickup_readings: "RentalReading",
        clock: "ClockService",
        rental_id: Optional[str] = None,
    ) -> None:
        """Constructor method for Rental class"""
        # Validate reservation
        from entities.reservation import Reservation

        if not isinstance(reservation, Reservation):
            raise TypeError("reservation must be an instance of Reservation class")

        # Validate pickup_token
        if not isinstance(pickup_token, str):
            raise TypeError("pickup_token must be a string")
        if not pickup_token:
            raise ValueError("pickup_token cannot be empty")

        # Validate pickup_readings
        from schemas.entities import RentalReading

        if not isinstance(pickup_readings, RentalReading):
            raise TypeError("pickup_readings must be an instance of RentalReading")

        # Validate clock
        from core.clock_service import ClockService

        if not isinstance(clock, ClockService):
            raise TypeError("clock must be an instance of ClockService")

        # Validate rental_id
        if rental_id is not None and not isinstance(rental_id, str):
            raise TypeError("rental_id must be a string")
        if rental_id == "":
            raise ValueError("rental_id cannot be empty")

        # Assign values
        self.__id = rental_id if rental_id is not None else str(uuid.uuid4())
        self.__reservation = reservation
        self.__pickup_token = pickup_token
        self.__pickup_readings = pickup_readings
        self.__return_readings: Optional["RentalReading"] = None
        self.__charges: Optional["RentalCharges"] = None
        self._clock = clock

    @property
    def id(self) -> str:
        """
        Getter for id property.

        Note: ID is auto-generated and immutable.
        """
        return self.__id

    @property
    def reservation(self) -> "Reservation":
        """Getter for reservation property"""
        return self.__reservation

    @property
    def pickup_token(self) -> str:
        """
        Getter for pickup_token property.

        Note: Used for idempotent pickup operations.
        """
        return self.__pickup_token

    @property
    def pickup_readings(self) -> "RentalReading":
        """Getter for pickup_readings property"""
        return self.__pickup_readings

    @property
    def return_readings(self) -> Optional["RentalReading"]:
        """Getter for return_readings property"""
        return self.__return_readings

    @property
    def charges(self) -> Optional["RentalCharges"]:
        """
        Getter for charges property.

        Note: Only available after complete_return() is called.
        """
        return self.__charges

    def is_returned(self) -> bool:
        """
        Check if rental has been returned.

        Returns:
            bool: True if return_readings exist, False otherwise.
        """
        return self.__return_readings is not None

    def complete_return(
        self,
        return_readings: "RentalReading",
        manual_damage_charge: float = 0.0,
    ) -> "RentalCharges":
        """
        Complete vehicle return and calculate all charges.

        This method:
        1. Records return readings (odometer, fuel, timestamp)
        2. Calculates the grace period (1 hour free after due time)
        3. Calculates late fees (hourly after the grace period)
        4. Calculates mileage overage (vs daily allowance)
        5. Calculates fuel refill charges
        6. Adds manual damage charges
        7. Returns itemized RentalCharges

        Args:
            return_readings (RentalReading): Odometer/fuel at return.
            manual_damage_charge (float): Optional damage assessment by agent.

        Returns:
            RentalCharges: Itemized breakdown of all charges.

        Raises:
            TypeError: If return_readings is not RentalReading instance.
            ValueError: If rental already returned or damage charge is negative.
        """
        # Validate return_readings
        from schemas.entities import RentalReading, RentalCharges

        if not isinstance(return_readings, RentalReading):
            raise TypeError("return_readings must be an instance of RentalReading")

        # Validate manual_damage_charge
        if not isinstance(manual_damage_charge, (int, float)):
            raise TypeError("manual_damage_charge must be a numeric value")
        if manual_damage_charge < 0:
            raise ValueError("manual_damage_charge cannot be negative")

        # Check if already returned
        if self.__return_readings is not None:
            raise ValueError("Rental has already been returned")

        # Store return readings
        self.__return_readings = return_readings

        # Calculations

        # Grace period calculation
        # Due time is end of return_date (23:59:59)
        rental_days = (
            self.__reservation.return_date - self.__reservation.pickup_date
        ).days
        due_datetime = self.__pickup_readings.timestamp + timedelta(days=rental_days)

        # Grace period ends 1 hour after due time
        grace_end_datetime = due_datetime + timedelta(hours=1)
        actual_return_datetime = return_readings.timestamp

        # Late fee calculation
        if actual_return_datetime > grace_end_datetime:
            late_seconds = (actual_return_datetime - grace_end_datetime).total_seconds()
            late_hours = math.ceil(late_seconds / 3600)  # Round up to next hour
            late_fee = late_hours * LATE_FEE_PER_HOUR
        else:
            late_fee = 0.0

        # Mileage overage calculation
        rental_days = (
            self.__reservation.return_date - self.__reservation.pickup_date
        ).days

        # Handle same-day rentals (minimum 1 day)
        if rental_days == 0:
            rental_days = 1

        allowed_km = rental_days * DAILY_KM_ALLOWANCE
        actual_km = return_readings.odometer - self.__pickup_readings.odometer
        overage_km = max(0, actual_km - allowed_km)
        mileage_overage_fee = overage_km * OVERAGE_PER_KM

        # Fuel refill calculation
        # Charge if fuel level is lower than at pickup
        fuel_difference = self.__pickup_readings.fuel_level - return_readings.fuel_level
        fuel_refill_fee = max(0, fuel_difference * FUEL_REFILL_RATE)

        # Create itemized charges
        self.__charges = RentalCharges(
            base_price=self.__reservation.total_price,
            late_fee=late_fee,
            mileage_overage_fee=mileage_overage_fee,
            fuel_refill_fee=fuel_refill_fee,
            damage_fee=manual_damage_charge,
        )

        return self.__charges

    def __str__(self) -> str:
        """String representation of Rental"""
        status = "returned" if self.is_returned() else "active"
        return (
            f"Rental(id={self.id}, reservation_id={self.reservation.id}, "
            f"pickup_token={self.pickup_token}, status={status})"
        )
