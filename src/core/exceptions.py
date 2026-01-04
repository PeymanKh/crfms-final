class VehicleNotAvailableError(Exception):
    pass


class ReturnDateBeforePickupDateError(Exception):
    def __init__(self, return_date, pickup_date):
        super().__init__(
            f"Return date {return_date} cannot be before pickup date {pickup_date}"
        )


class InvalidReservationStatusForCancellationError(Exception):
    def __init__(self, status):
        message = f"Reservation with status '{status}' cannot be cancelled"
        super().__init__(message)


class PaymentRequiredForPickupError(Exception):
    def __init__(self, reservation_id: str):
        super().__init__(
            f"Vehicle {reservation_id} cannot be picked up before payment."
        )


class ReservationNotApprovedError(Exception):
    def __init__(self, reservation_id: str):
        super().__init__(f"Reservation {reservation_id} is not approved yet.")


class ReservationNotFoundError(Exception):
    def __init__(self, reservation_id: str):
        super().__init__(f"Reservation with ID {reservation_id} not found.")
