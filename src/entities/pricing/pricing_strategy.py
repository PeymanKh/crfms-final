"""
This module implements the Context class for pricing strategies.
This is the Context component of the Strategy design pattern.

The Context class manages pricing strategy selection and delegates
price calculation to the selected strategy.

Business Logic:
    - First reservation (0 previous): FirstOrderStrategy (15% discount)
    - Every 5th reservation: LoyaltyStrategy (10% discount)
    - All other cases: DailyStrategy (no discount)

Author: Peyman Khodabandehlouei
Date: 08-11-2025
"""

from datetime import date
from typing import Optional, List, TYPE_CHECKING


if TYPE_CHECKING:
    from entities.user import Customer
    from entities.vehicle import Vehicle
    from entities.pricing import Strategy
    from entities.reservation import AddOn, InsuranceTier


class PricingStrategy:
    """
    Context class that uses a pricing strategy to calculate reservation prices.

    This class receives a customer and automatically defines the pricing strategy based
    on their previous reservations:
        - First reservation: FirstOrderStrategy (15% off)
        - Every 5th reservation: LoyaltyStrategy (10% off)
        - All others: DailyStrategy (no discount)

    Args:
        customer (Customer): The customer making the reservation.

    Raises:
        TypeError: If customer is not an instance of Customer class.
    """

    def __init__(self, customer: "Customer") -> None:
        """
        Initialize the PricingContext with automatic strategy selection.

        Args:
            customer (Customer): The customer making the reservation.

        Raises:
            TypeError: If customer is not an instance of Customer class.
        """
        from entities.user import Customer
        from entities.pricing import (
            DailyStrategy,
            FirstOrderStrategy,
            LoyaltyStrategy,
        )

        # Validation
        if not isinstance(customer, Customer):
            raise TypeError("customer must be an instance of Customer class")

        # Business logic - Automatic strategy selection
        reservations_count = len(customer.reservations)

        if reservations_count == 0:
            # First order - 15% discount
            self.__strategy = FirstOrderStrategy()
        elif (reservations_count + 1) % 5 == 0:
            # Every 5th order - 10% loyalty discount
            self.__strategy = LoyaltyStrategy()
        else:
            # Regular pricing - no discount
            self.__strategy = DailyStrategy()

    @property
    def strategy(self) -> "Strategy":
        """
        Getter for the current strategy.

        Returns:
            Strategy: The current pricing strategy.
        """
        return self.__strategy

    @strategy.setter
    def strategy(self, strategy: "Strategy") -> None:
        """
        Setter for the strategy, allows changing strategy at runtime.

        Args:
            strategy (Strategy): The new pricing strategy to use.

        Raises:
            TypeError: If strategy is not an instance of Strategy interface.
        """
        from entities.pricing import Strategy

        if not isinstance(strategy, Strategy):
            raise TypeError("strategy must be an instance of Strategy interface")

        self.__strategy = strategy

    def calculate_price(
        self,
        vehicle: "Vehicle",
        insurance_tier: "InsuranceTier",
        pickup_date: date,
        return_date: date,
        add_ons: Optional[List["AddOn"]] = None,
    ) -> float:
        """
        Calculate the total price using the current strategy.

        Delegates the price calculation to the strategy object without
        knowing the implementation details of the pricing algorithm.

        Args:
            vehicle (Vehicle): The vehicle being rented.
            insurance_tier (InsuranceTier): The selected insurance tier.
            pickup_date (date): The rental pickup date.
            return_date (date): The rental return date.
            add_ons (Optional[List[AddOn]]): Optional list of add-ons. Defaults to None.

        Returns:
            float: The total calculated price for the reservation.

        Raises:
            TypeError: If any parameter has an incorrect type.
            ValueError: If any parameter violates business rules.
        """
        return self.__strategy.calculate(
            vehicle=vehicle,
            insurance_tier=insurance_tier,
            pickup_date=pickup_date,
            return_date=return_date,
            add_ons=add_ons,
        )
