"""
Test rental flow module

This module contains unit tests for the rental flow. The main goal of this module is to test
the rental flow which is as follows:
    1. A customer reserves an available vehicle.
    2. The customer attempts to pick up the vehicle before approval by an agent and fails.
    3. An agent approves the reservation.
    4. The customer attempts to pick up the vehicle before making a payment and fails.
    5. The customer pays for the reservation.
    6. The customer picks up the vehicle successfully.
"""

import pytest

from core import PaymentRequiredForPickupError, ReservationNotApprovedError


def test_rental_flow_success(
    get_customer,
    get_main_branch,
    get_active_agent,
    get_economy_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Check vehicle status before reservation
    assert get_economy_vehicle.status == "available"

    # Customer makes a reservation
    get_customer.create_reservation(
        vehicle=get_economy_vehicle,
        insurance_tier=get_premium_insurance_tier,
        add_ons=[get_gps_addon],
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    # Check vehicle status after reservation
    assert get_economy_vehicle.status == "reserved"

    # Access reservation id
    reservation_id: str = get_customer.reservations[0].id

    # Test ReservationNotApprovedError
    with pytest.raises(ReservationNotApprovedError):
        get_customer.pickup_vehicle(reservation_id)

    # Approve reservation
    get_active_agent.approve_reservation(get_customer.reservations[0])
    assert get_customer.reservations[0].status == "approved"

    # Test invoice status
    assert get_customer.reservations[0].invoice.status == "pending"

    # Test PaymentRequiredForPickupError
    with pytest.raises(PaymentRequiredForPickupError):
        get_customer.pickup_vehicle(reservation_id)

    # Make payment
    get_customer.make_creditcard_payment(
        get_customer.reservations[0], "1234 1234 1234 1234", "123", "12/30"
    )
    assert get_customer.reservations[0].invoice.status == "completed"

    # Pick up vehicle successfully
    get_customer.pickup_vehicle(reservation_id)
    assert get_economy_vehicle.status == "picked_up"

    # Return vehicle successfully
    get_customer.return_vehicle(reservation_id)
    assert get_economy_vehicle.status == "available"
