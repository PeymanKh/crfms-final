"""
Pricing Calculator Utility

Author: Peyman Khodabandehlouei
Date: 06-01-2026
"""

from datetime import date
from typing import List, Literal

PricingStrategyType = Literal["daily", "first_order", "loyalty"]


def calculate_rental_days(pickup_date: date, return_date: date) -> int:
    """
    Calculate number of rental days.

    Args:
        pickup_date (date): Pickup date
        return_date (date): Return date

    Returns:
        int: Number of rental days
    """
    return (return_date - pickup_date).days


def calculate_base_price(
    vehicle_price_per_day: float,
    insurance_price_per_day: float,
    addon_prices_per_day: List[float],
    rental_days: int,
) -> float:
    """
    Calculate base price without any discounts.

    Formula: (vehicle + insurance + sum(addons)) × days

    Args:
        vehicle_price_per_day (float): Vehicle daily rate
        insurance_price_per_day (float): Insurance daily rate
        addon_prices_per_day (List[float]): List of addon daily rates
        rental_days (int): Number of rental days

    Returns:
        float: Base price before discounts
    """
    daily_rate = (
        vehicle_price_per_day + insurance_price_per_day + sum(addon_prices_per_day)
    )
    return daily_rate * rental_days


def apply_discount(base_price: float, discount_percentage: float) -> float:
    """
    Apply discount to base price.

    Args:
        base_price (float): Price before discount
        discount_percentage (float): Discount as decimal (0.15 = 15%)

    Returns:
        float: Price after discount
    """
    discount_amount = base_price * discount_percentage
    return base_price - discount_amount


def calculate_total_price(
    vehicle_price_per_day: float,
    insurance_price_per_day: float,
    addon_prices_per_day: List[float],
    pickup_date: date,
    return_date: date,
    strategy_type: PricingStrategyType,
) -> float:
    """
    Calculate total reservation price with appropriate discount strategy.

    Pricing Strategies:
    - daily: No discount (regular customer)
    - first_order: 15% discount (first reservation)
    - loyalty: 10% discount (every 5th reservation)

    Args:
        vehicle_price_per_day (float): Vehicle daily rate
        insurance_price_per_day (float): Insurance daily rate
        addon_prices_per_day (List[float]): List of addon daily rates
        pickup_date (date): Pickup date
        return_date (date): Return date
        strategy_type (PricingStrategyType): Which pricing strategy to apply

    Returns:
        float: Total price with discount applied
    """
    # Calculate rental days
    rental_days = calculate_rental_days(pickup_date, return_date)

    # Calculate base price
    base_price = calculate_base_price(
        vehicle_price_per_day=vehicle_price_per_day,
        insurance_price_per_day=insurance_price_per_day,
        addon_prices_per_day=addon_prices_per_day,
        rental_days=rental_days,
    )

    # Apply discount based on strategy
    if strategy_type == "first_order":
        return apply_discount(base_price, 0.15)  # 15% off
    elif strategy_type == "loyalty":
        return apply_discount(base_price, 0.10)  # 10% off
    else:  # daily
        return base_price  # No discount


def determine_pricing_strategy(reservation_count: int) -> PricingStrategyType:
    """
    Determine which pricing strategy to use based on customer's reservation count.

    Business Logic:
    - First reservation (count = 0): first_order (15% off)
    - Every 5th reservation (count+1 divisible by 5): loyalty (10% off)
    - All others: daily (no discount)

    Args:
        reservation_count (int): Number of existing reservations customer has

    Returns:
        PricingStrategyType: The pricing strategy to use
    """
    if reservation_count == 0:
        return "first_order"
    elif (reservation_count + 1) % 5 == 0:
        return "loyalty"
    else:
        return "daily"
