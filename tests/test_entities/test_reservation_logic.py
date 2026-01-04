"""
Test rental flow module

This module contains unit tests for the rental business logic.
Here is a list of the available tests:
    1. Reserve an Available vehicle.
    2. Reserve a RESERVED vehicle.
    3. Reserve a PICKED_UP vehicle.
    4. Reserve a car with return date before pickup date.
    5. Cancel a pending reservation.
    6. Cancel an approved reservation.
    7. Cancel a completed reservation.
    9. Cancel a picked-up reservation.

Author: Peyman Khodabandehlouei
Date: 02-12-2025
"""

import pytest

from schemas.entities import VehicleStatus, ReservationStatus
from core import (
    ReturnDateBeforePickupDateError,
    VehicleNotAvailableError,
    InvalidReservationStatusForCancellationError,
)


def test_create_reservation_when_vehicle_available_success(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    """Test reservation of an available vehicle."""
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Create reservation
    get_customer.create_reservation(
        vehicle=get_compact_vehicle,
        insurance_tier=get_premium_insurance_tier,
        add_ons=[get_gps_addon],
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    assert len(get_customer.reservations) == 1
    assert get_customer.reservations[0].status == ReservationStatus.PENDING.value
    assert get_customer.reservations[0].vehicle.status == VehicleStatus.RESERVED.value


def test_create_reservation_when_vehicle_reserved_error(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    """Test reservation of a reserved vehicle error."""
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Change vehicle status to reserved
    get_compact_vehicle.status = VehicleStatus.RESERVED

    # Create reservation
    with pytest.raises(VehicleNotAvailableError):
        get_customer.create_reservation(
            vehicle=get_compact_vehicle,
            insurance_tier=get_premium_insurance_tier,
            add_ons=[get_gps_addon],
            pickup_branch=get_main_branch,
            return_branch=get_main_branch,
            pickup_date=pickup_date,
            return_date=return_date,
        )


def test_create_reservation_when_vehicle_pickedup_error(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    """Test reservation of a reserved vehicle error."""
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Change vehicle status to reserved
    get_compact_vehicle.status = VehicleStatus.PICKED_UP

    # Create reservation
    with pytest.raises(VehicleNotAvailableError):
        get_customer.create_reservation(
            vehicle=get_compact_vehicle,
            insurance_tier=get_premium_insurance_tier,
            add_ons=[get_gps_addon],
            pickup_branch=get_main_branch,
            return_branch=get_main_branch,
            pickup_date=pickup_date,
            return_date=return_date,
        )


def test_create_reservation_when_return_date_before_pickup_date_error(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    """Test reservation of a vehicle with return date before pickup date error."""
    # Get pickup and return dates
    return_date, pickup_date = get_pickup_and_return_dates

    with pytest.raises(ReturnDateBeforePickupDateError):

        # Create reservation
        get_customer.create_reservation(
            vehicle=get_compact_vehicle,
            insurance_tier=get_premium_insurance_tier,
            add_ons=[get_gps_addon],
            pickup_branch=get_main_branch,
            return_branch=get_main_branch,
            pickup_date=pickup_date,
            return_date=return_date,
        )


def test_canceling_pending_reservation_success(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    # Create date objects for pickup and return dates (Total 3 days)
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Create reservation
    get_customer.create_reservation(
        vehicle=get_compact_vehicle,
        insurance_tier=get_premium_insurance_tier,
        add_ons=[get_gps_addon],
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    # Cancel the reservation
    reservation = get_customer.reservations[0]
    get_customer.cancel_reservation(reservation.id)

    assert reservation.status == ReservationStatus.CANCELLED.value


def test_canceling_approved_reservation_success(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Create reservation
    get_customer.create_reservation(
        vehicle=get_compact_vehicle,
        insurance_tier=get_premium_insurance_tier,
        add_ons=[get_gps_addon],
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    # Approve the reservation
    reservation = get_customer.reservations[0]
    reservation.status = ReservationStatus.APPROVED

    # Cancel the reservation
    get_customer.cancel_reservation(reservation.id)

    assert reservation.status == ReservationStatus.CANCELLED.value


def test_canceling_completed_reservation_error(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Create reservation
    get_customer.create_reservation(
        vehicle=get_compact_vehicle,
        insurance_tier=get_premium_insurance_tier,
        add_ons=[get_gps_addon],
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    # Approve the reservation
    reservation = get_customer.reservations[0]
    reservation.status = ReservationStatus.COMPLETED

    assert reservation.status == ReservationStatus.COMPLETED.value

    # Cancel the reservation
    with pytest.raises(InvalidReservationStatusForCancellationError):
        get_customer.cancel_reservation(reservation.id)


def test_canceling_pickedup_reservation_error(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Create reservation
    get_customer.create_reservation(
        vehicle=get_compact_vehicle,
        insurance_tier=get_premium_insurance_tier,
        add_ons=[get_gps_addon],
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    # Approve the reservation
    reservation = get_customer.reservations[0]
    reservation.status = ReservationStatus.PICKED_UP

    assert reservation.status == ReservationStatus.PICKED_UP.value

    # Cancel the reservation
    with pytest.raises(InvalidReservationStatusForCancellationError):
        get_customer.cancel_reservation(reservation.id)
