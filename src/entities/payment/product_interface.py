"""
This module implements interface for application's payment product.
This is the first component of the Factory design pattern for the payment service.

Author: Peyman Khodabandehlouei
Date: 08-11-2025
"""

from abc import ABC, abstractmethod


class PaymentInterface(ABC):
    """This class is an abstract implementation of application's payment products"""

    @abstractmethod
    def validate_payment_details(self) -> bool:
        """Validates payment details"""
        pass

    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        """Processes the transaction"""
        pass

    @abstractmethod
    def generate_receipt(self, amount: float, success: bool) -> str:
        """Generates a receipt for the payment"""
        pass
