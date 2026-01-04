"""
This module implements concrete payment products that we have.
This is the second component of the Factory design pattern for the payment service.

Author: Peyman Khodabandehlouei
Date: 08-11-2025
"""

from entities.payment import PaymentInterface


class CreditcardPayment(PaymentInterface):
    """Concrete implementation of creditcard payment product"""

    def __init__(self, card_number: str, cvv: str, expiry: str):
        """
        Constructor for CreditcardPayment.

        Args:
            card_number (str): Credit card number.
            cvv (str): Card CVV code.
            expiry (str): Card expiry date.

        Raises:
            TypeError: If any parameter is not a string.
            ValueError: If any parameter is empty or invalid.
        """
        # Validate types
        if not isinstance(card_number, str):
            raise TypeError("card_number must be a string")
        if not isinstance(cvv, str):
            raise TypeError("cvv must be a string")
        if not isinstance(expiry, str):
            raise TypeError("expiry must be a string")

        # Validate values
        if not card_number:
            raise ValueError("card_number cannot be empty")
        if not cvv:
            raise ValueError("cvv cannot be empty")
        if not expiry:
            raise ValueError("expiry cannot be empty")

        self.__card_number = card_number
        self.__cvv = cvv
        self.__expiry = expiry

    def validate_payment_details(self) -> bool:
        print(
            f"from payment product: Validating Card ending with {self.__card_number[-4:]}"
        )
        return True

    def process_payment(self, amount: float) -> bool:
        print(
            f"from payment product: Processing ${amount:,} with card ending with {self.__card_number[-4:]}"
        )
        return True

    def generate_receipt(self, amount: float, success: bool) -> str:
        status = "from payment product: successful" if success else "failed"

        return f"Payment of ${amount:,} with card ending with {self.__card_number[-4:]} was {status}"


class PayPalPayment(PaymentInterface):
    """Concrete product for PayPal payment"""

    def __init__(self, email: str, auth_token: str):
        """
        Constructor for PayPalPayment.

        Args:
            email (str): PayPal account email.
            auth_token (str): PayPal authentication token.

        Raises:
            TypeError: If any parameter is not a string.
            ValueError: If any parameter is empty.
        """
        # Validate types
        if not isinstance(email, str):
            raise TypeError("email must be a string")
        if not isinstance(auth_token, str):
            raise TypeError("auth_token must be a string")

        # Validate values
        if not email:
            raise ValueError("email cannot be empty")
        if not auth_token:
            raise ValueError("auth_token cannot be empty")

        self.__email = email
        self.__auth_token = auth_token

    def validate_payment_details(self) -> bool:
        print(
            f"from payment product: Validating PayPal account with email {self.__email}"
        )
        return True

    def process_payment(self, amount: float) -> bool:
        print(
            f"from payment product: Processing ${amount:,} with PayPal account {self.__email}"
        )
        return False

    def generate_receipt(self, amount: float, success: bool) -> str:
        status = "successful" if success else "failed"
        return f"Payment of ${amount:,} with PayPal account {self.__email} was {status}"
