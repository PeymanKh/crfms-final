"""
This module implements concrete payment factories.
This is the last component of the Factory design pattern for the payment service.

Author: Peyman Khodabandehlouei
Date: 08-11-2025
"""

from typing import TYPE_CHECKING
from domain.payment import PaymentFactoryInterface, CreditcardPayment, PayPalPayment


if TYPE_CHECKING:
    from domain.payment import PaymentInterface


class CreditCardPaymentCreator(PaymentFactoryInterface):
    """Concrete creator for creditcard payment"""

    def __init__(self, card_number: str, cvv: str, expiry: str):
        self.card_number = card_number
        self.cvv = cvv
        self.expiry = expiry

    def create_payment_product(self) -> "PaymentInterface":
        return CreditcardPayment(
            card_number=self.card_number, cvv=self.cvv, expiry=self.expiry
        )


class PaypalPaymentCreator(PaymentFactoryInterface):
    """Concrete creator for PayPal payment"""

    def __init__(self, email: str, auth_token: str):
        self.email = email
        self.auth_token = auth_token

    def create_payment_product(self) -> "PaymentInterface":
        return PayPalPayment(email=self.email, auth_token=self.auth_token)
