"""
This module provides public API for Pricing domain including Addon,
InsuranceTier, Invoice, and Reservation.

Author: Peyman Khodabandehlouei
"""

# Import modules
from domain.pricing.strategy_interface import Strategy
from domain.pricing.pricing_strategy import PricingStrategy
from domain.pricing.concrete_strategies import (
    DailyStrategy,
    FirstOrderStrategy,
    LoyaltyStrategy,
)


# Public API
__all__ = [
    "Strategy",
    "DailyStrategy",
    "PricingStrategy",
    "LoyaltyStrategy",
    "FirstOrderStrategy",
]
