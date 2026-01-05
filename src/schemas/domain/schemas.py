"""
Pydantic models used by application domain.

Author: Peyman Khodabandehlouei
"""

from datetime import datetime
from pydantic import BaseModel, computed_field, Field


class RentalCharges(BaseModel):
    """
    Breakdown of rental charges.

    Note: total is a computed automatically.
    """

    base_price: float
    late_fee: float
    mileage_overage_fee: float
    fuel_refill_fee: float
    damage_fee: float

    @computed_field
    @property
    def total(self) -> float:
        """Total charges including all fees"""
        return (
            self.base_price
            + self.late_fee
            + self.mileage_overage_fee
            + self.fuel_refill_fee
            + self.damage_fee
        )


class RentalReading(BaseModel):
    """Odometer and fuel readings at pickup/return"""

    odometer: float
    fuel_level: float = Field(ge=0, le=1)
    timestamp: datetime
