"""
This module implements concrete pricing strategies.
There are three types of pricing strategies:
    - Daily Strategy: normal price from daily base price
    - First Order Strategy: 15% off on first order
    - Loyalty Strategy: 10% off on fifth orders

Business Logic:
    - Pickup date must be before or equal to return date.
    - Pickup date cannot be in the past.

Author: Peyman Khodabandehlouei
Date: 08-11-2025
"""

from datetime import date
from typing import Optional, List, TYPE_CHECKING

from domain.pricing import Strategy


if TYPE_CHECKING:
    from core import ClockService
    from domain.vehicle import Vehicle
    from domain.reservation import AddOn, InsuranceTier


class DailyStrategy(Strategy):
    """Concrete strategy for first order pricing with no discount"""

    def calculate(
        self,
        vehicle: "Vehicle",
        insurance_tier: "InsuranceTier",
        pickup_date: date,
        return_date: date,
        add_ons: Optional[List["AddOn"]] = None,
        clock: Optional["ClockService"] = None,
    ) -> float:
        """
        Calculate the total price with no discount.

        Args:
            vehicle (Vehicle): The vehicle being rented.
            insurance_tier (InsuranceTier): The selected insurance tier.
            pickup_date (date): The rental pickup date.
            return_date (date): The rental return date.
            add_ons (Optional[List[AddOn]]): Optional list of add-ons.
            clock (Optional[ClockService]): Optional clock service for time-based calculations.

        Returns:
            float: The total calculated price.
        """
        from core.clock_service import SystemClock

        clock = clock or SystemClock()

        # Validate vehicle
        from domain.vehicle import Vehicle

        if not isinstance(vehicle, Vehicle):
            raise TypeError("vehicle must be an instance of Vehicle class.")

        # Validate insurance tier
        from domain.reservation import InsuranceTier

        if not isinstance(insurance_tier, InsuranceTier):
            raise TypeError(
                "insurance_tier must be an instance of InsuranceTier class."
            )

        # Validate pickup and return dates
        if not isinstance(pickup_date, date):
            raise TypeError("pickup_date must be an instance of date class.")
        if not isinstance(return_date, date):
            raise TypeError("return_date must be an instance of date class.")

        if pickup_date > return_date:
            raise ValueError("pickup_date must be before or equal to return_date.")
        if return_date < pickup_date:
            raise ValueError("return_date must be after or equal to pickup_date.")

        if pickup_date < clock.today():
            raise ValueError("pickup_date cannot be in the past.")

        # Validate addons
        if add_ons is None:
            add_ons = []

        from domain.reservation import AddOn

        if not isinstance(add_ons, list):
            raise TypeError("add_ons must be a list of AddOn instances.")
        if not all(isinstance(add_on, AddOn) for add_on in add_ons):
            raise TypeError("All add-ons must be instances of AddOn class.")

        # Business logic
        # Calculate rental days
        rental_days = (return_date - pickup_date).days

        # Calculate vehicle cost
        vehicle_cost = vehicle.price_per_day * rental_days

        # Calculate insurance cost
        insurance_cost = insurance_tier.price_per_day * rental_days

        # Calculate add-ons cost
        addons_cost = sum(addon.price_per_day for addon in add_ons) * rental_days

        # Calculate total price
        total_price = vehicle_cost + insurance_cost + addons_cost

        return total_price


class FirstOrderStrategy(Strategy):
    """Concrete strategy for first order pricing with 15% discount"""

    def calculate(
        self,
        vehicle: "Vehicle",
        insurance_tier: "InsuranceTier",
        pickup_date: date,
        return_date: date,
        add_ons: Optional[List["AddOn"]] = None,
        clock: Optional["ClockService"] = None,
    ) -> float:
        """
        Calculate the total price with 15% first order discount.

        Args:
            vehicle (Vehicle): The vehicle being rented.
            insurance_tier (InsuranceTier): The selected insurance tier.
            pickup_date (date): The rental pickup date.
            return_date (date): The rental return date.
            add_ons (Optional[List[AddOn]]): Optional list of add-ons.
            clock (Optional[ClockService]): Optional clock service for time-based calculations.

        Returns:
            float: The total calculated price with 15% discount applied.
        """
        from core.clock_service import SystemClock

        clock = clock or SystemClock()

        # Validate vehicle
        from domain.vehicle import Vehicle

        if not isinstance(vehicle, Vehicle):
            raise TypeError("vehicle must be an instance of Vehicle class.")

        # Validate insurance tier
        from domain.reservation import InsuranceTier

        if not isinstance(insurance_tier, InsuranceTier):
            raise TypeError(
                "insurance_tier must be an instance of InsuranceTier class."
            )

        # Validate pickup and return dates
        if not isinstance(pickup_date, date):
            raise TypeError("pickup_date must be an instance of date class.")
        if not isinstance(return_date, date):
            raise TypeError("return_date must be an instance of date class.")

        if pickup_date > return_date:
            raise ValueError("pickup_date must be before or equal to return_date.")
        if return_date < pickup_date:
            raise ValueError("return_date must be after or equal to pickup_date.")

        if pickup_date < clock.today():
            raise ValueError("pickup_date cannot be in the past.")

        # Validate addons
        if add_ons is None:
            add_ons = []
        from domain.reservation import AddOn

        if not isinstance(add_ons, list):
            raise TypeError("add_ons must be a list of AddOn instances.")
        if not all(isinstance(add_on, AddOn) for add_on in add_ons):
            raise TypeError("All add-ons must be instances of AddOn class.")

        # Business logic
        # Calculate rental days
        rental_days = (return_date - pickup_date).days

        # Calculate vehicle cost
        vehicle_cost = vehicle.price_per_day * rental_days

        # Calculate insurance cost
        insurance_cost = insurance_tier.price_per_day * rental_days

        # Calculate add-ons cost
        addons_cost = sum(addon.price_per_day for addon in add_ons) * rental_days

        # Calculate subtotal
        subtotal = vehicle_cost + insurance_cost + addons_cost

        # Apply 15% discount
        discount = subtotal * 0.15
        total_price = subtotal - discount

        return total_price


class LoyaltyStrategy(Strategy):
    """Concrete strategy for loyalty pricing with 10% discount on every 5th order"""

    def calculate(
        self,
        vehicle: "Vehicle",
        insurance_tier: "InsuranceTier",
        pickup_date: date,
        return_date: date,
        add_ons: Optional[List["AddOn"]] = None,
        clock: Optional["ClockService"] = None,
    ) -> float:
        """
        Calculate the total price with 10% loyalty discount.

        Args:
            vehicle (Vehicle): The vehicle being rented.
            insurance_tier (InsuranceTier): The selected insurance tier.
            pickup_date (date): The rental pickup date.
            return_date (date): The rental return date.
            add_ons (Optional[List[AddOn]]): Optional list of add-ons.
            clock (Optional[ClockService]): Optional clock service for time-based calculations.

        Returns:
            float: The total calculated price with 10% discount applied.
        """
        from core.clock_service import SystemClock

        clock = clock or SystemClock()

        # Validate vehicle
        from domain.vehicle import Vehicle

        if not isinstance(vehicle, Vehicle):
            raise TypeError("vehicle must be an instance of Vehicle class.")

        # Validate insurance tier
        from domain.reservation import InsuranceTier

        if not isinstance(insurance_tier, InsuranceTier):
            raise TypeError(
                "insurance_tier must be an instance of InsuranceTier class."
            )

        # Validate pickup and return dates
        if not isinstance(pickup_date, date):
            raise TypeError("pickup_date must be an instance of date class.")
        if not isinstance(return_date, date):
            raise TypeError("return_date must be an instance of date class.")

        if pickup_date > return_date:
            raise ValueError("pickup_date must be before or equal to return_date.")
        if return_date < pickup_date:
            raise ValueError("return_date must be after or equal to pickup_date.")

        if pickup_date < clock.today():
            raise ValueError("pickup_date cannot be in the past.")

        # Validate addons
        if add_ons is None:
            add_ons = []
        from domain.reservation import AddOn

        if not isinstance(add_ons, list):
            raise TypeError("add_ons must be a list of AddOn instances.")
        if not all(isinstance(add_on, AddOn) for add_on in add_ons):
            raise TypeError("All add-ons must be instances of AddOn class.")

        # Business logic
        # Calculate rental days
        rental_days = (return_date - pickup_date).days

        # Calculate vehicle cost
        vehicle_cost = vehicle.price_per_day * rental_days

        # Calculate insurance cost
        insurance_cost = insurance_tier.price_per_day * rental_days

        # Calculate add-ons cost
        addons_cost = sum(addon.price_per_day for addon in add_ons) * rental_days

        # Calculate subtotal
        subtotal = vehicle_cost + insurance_cost + addons_cost

        # Apply 10% loyalty discount
        discount = subtotal * 0.10
        total_price = subtotal - discount

        return total_price
