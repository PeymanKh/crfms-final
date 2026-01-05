"""
This module implements interface for application's payment factory.
This is the third component of the Factory design pattern for the payment service.

Author: Peyman Khodabandehlouei
Date: 08-11-2025
"""

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from domain.payment import PaymentInterface


class PaymentFactoryInterface(ABC):
    """This class is an abstract implementation of application's payment factory"""

    @abstractmethod
    def create_payment_product(self) -> "PaymentInterface":
        """Factory method to return a payment object"""
        pass

    def execute_payment(self, amount: float) -> str:
        """Main business logic for payment execution"""
        # Create payment service
        payment_service = self.create_payment_product()

        # Validate payment details
        validation_result = payment_service.validate_payment_details()

        if validation_result:
            # Execute payment
            payment_service.process_payment(amount)
            # Generate and return receipt
            return payment_service.generate_receipt(amount, True)
        else:
            # Generate and return receipt
            return payment_service.generate_receipt(amount, False)
