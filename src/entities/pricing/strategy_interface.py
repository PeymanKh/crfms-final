"""
This module implements interface for application's pricing strategies.
This is the first component of the Strategy design pattern.

Author: Peyman Khodabandehlouei
Date: 08-11-2025
"""

from datetime import date
from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING


if TYPE_CHECKING:
    from entities.vehicle import Vehicle
    from entities.reservation import AddOn, InsuranceTier


class Strategy(ABC):
    """
    Abstract base class for pricing calculation strategies.

    This interface defines the Strategy pattern for calculating reservation prices.
    Concrete strategies must implement the calculate() method with their specific
    pricing algorithms.
    """

    @abstractmethod
    def calculate(
        self,
        vehicle: "Vehicle",
        insurance_tier: "InsuranceTier",
        pickup_date: date,
        return_date: date,
        add_ons: Optional[List["AddOn"]] = None,
    ) -> float:
        """
        Abstract method to calculate the total price of a reservation.

        Args:
            vehicle (Vehicle): The vehicle being rented.
            insurance_tier (InsuranceTier): The selected insurance tier.
            pickup_date (date): The rental pickup date.
            return_date (date): The rental return date.
            add_ons (Optional[List[AddOn]]): Optional list of add-ons. Defaults to None.

        Returns:
            float: The total calculated price for the reservation.
        """
        pass
