"""
Test rental charge calculations.

This module tests the business logic for:
    1. Grace period (1 hour free after due time)
    2. Late fees ($10/hour after grace)
    3. Mileage overage (200km/day allowance, $0.50/km over)
    4. Fuel refill charges (proportional to difference)
    5. Manual damage charges

Author: Peyman Khodabandehlouei
Date: 04-01-2026
"""

import pytest


def test_return_within_grace_period_no_late_fee(
    get_customer,
    get_main_branch,
    get_active_agent,
    get_economy_vehicle,
    get_basic_insurance_tier,
    get_pickup_and_return_dates,
    fake_clock,
):
    """Test that returning within grace period (1 hour) incurs no late fee"""
    pickup_date, return_date = get_pickup_and_return_dates

    # Create and approve reservation
    reservation = get_customer.create_reservation(
        vehicle=get_economy_vehicle,
        insurance_tier=get_basic_insurance_tier,
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
        clock=fake_clock,
    )

    get_active_agent.approve_reservation(reservation)
    get_customer.make_creditcard_payment(
        reservation, "1234123412341234", "123", "12/30"
    )

    # Pickup
    get_customer.pickup_vehicle(
        reservation_id=reservation.id,
        pickup_token="token-1",
        odometer=12500.0,
        fuel_level=0.8,
        clock=fake_clock,
    )

    # Advance to 50 minutes after due time (within grace period)
    fake_clock.advance(days=3, minutes=50)

    # Return
    charges = get_customer.return_vehicle(
        reservation_id=reservation.id,
        odometer=13100.0,
        fuel_level=0.8,
        clock=fake_clock,
    )

    assert charges.late_fee == 0.0, "No late fee within grace period"


def test_return_2_hours_late_incurs_late_fee(
    get_customer,
    get_main_branch,
    get_active_agent,
    get_economy_vehicle,
    get_basic_insurance_tier,
    get_pickup_and_return_dates,
    fake_clock,
):
    """Test that returning 1 hour after grace period incurs $10 late fee"""
    pickup_date, return_date = get_pickup_and_return_dates

    # Create and approve reservation
    reservation = get_customer.create_reservation(
        vehicle=get_economy_vehicle,
        insurance_tier=get_basic_insurance_tier,
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
        clock=fake_clock,
    )

    get_active_agent.approve_reservation(reservation)
    get_customer.make_creditcard_payment(
        reservation, "1234123412341234", "123", "12/30"
    )

    # Pickup
    get_customer.pickup_vehicle(
        reservation_id=reservation.id,
        pickup_token="token-2",
        odometer=12500.0,
        fuel_level=0.8,
        clock=fake_clock,
    )

    # Advance 3 days + 2 hours (1 hour past grace = 1 hour late)
    fake_clock.advance(days=3, hours=2)

    # Return
    charges = get_customer.return_vehicle(
        reservation_id=reservation.id,
        odometer=13100.0,
        fuel_level=0.8,
        clock=fake_clock,
    )

    assert charges.late_fee == 10.0, "1 hour past grace = $10"


def test_mileage_overage_calculation(
    get_customer,
    get_main_branch,
    get_active_agent,
    get_economy_vehicle,
    get_basic_insurance_tier,
    get_pickup_and_return_dates,
    fake_clock,
):
    """Test mileage overage: 3 days = 600km allowance, drive 700km = 100km over = $50"""
    pickup_date, return_date = get_pickup_and_return_dates

    reservation = get_customer.create_reservation(
        vehicle=get_economy_vehicle,
        insurance_tier=get_basic_insurance_tier,
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
        clock=fake_clock,
    )

    get_active_agent.approve_reservation(reservation)
    get_customer.make_creditcard_payment(
        reservation, "1234123412341234", "123", "12/30"
    )

    get_customer.pickup_vehicle(
        reservation_id=reservation.id,
        pickup_token="token-3",
        odometer=12500.0,
        fuel_level=0.8,
        clock=fake_clock,
    )

    fake_clock.advance(days=3)

    # Return with 700km driven (100km over allowance)
    charges = get_customer.return_vehicle(
        reservation_id=reservation.id,
        odometer=13200.0,  # 700km driven
        fuel_level=0.8,
        clock=fake_clock,
    )

    assert charges.mileage_overage_fee == 50.0, "100km overage * $0.50 = $50"


def test_fuel_refill_charge(
    get_customer,
    get_main_branch,
    get_active_agent,
    get_economy_vehicle,
    get_basic_insurance_tier,
    get_pickup_and_return_dates,
    fake_clock,
):
    """Test fuel charge: pickup at 0.8, return at 0.5 = 0.3 difference = $15"""
    pickup_date, return_date = get_pickup_and_return_dates

    reservation = get_customer.create_reservation(
        vehicle=get_economy_vehicle,
        insurance_tier=get_basic_insurance_tier,
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
        clock=fake_clock,
    )

    get_active_agent.approve_reservation(reservation)
    get_customer.make_creditcard_payment(
        reservation, "1234123412341234", "123", "12/30"
    )

    get_customer.pickup_vehicle(
        reservation_id=reservation.id,
        pickup_token="token-4",
        odometer=12500.0,
        fuel_level=0.8,
        clock=fake_clock,
    )

    fake_clock.advance(days=3)

    charges = get_customer.return_vehicle(
        reservation_id=reservation.id,
        odometer=13100.0,
        fuel_level=0.5,  # 0.3 less fuel
        clock=fake_clock,
    )

    assert charges.fuel_refill_fee == pytest.approx(
        15.0
    ), "0.3 fuel difference * $50 = $15"  # 👈 FIX


def test_manual_damage_charge(
    get_customer,
    get_main_branch,
    get_active_agent,
    get_economy_vehicle,
    get_basic_insurance_tier,
    get_pickup_and_return_dates,
    fake_clock,
):
    """Test manual damage charge added by agent"""
    pickup_date, return_date = get_pickup_and_return_dates

    reservation = get_customer.create_reservation(
        vehicle=get_economy_vehicle,
        insurance_tier=get_basic_insurance_tier,
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
        clock=fake_clock,
    )

    get_active_agent.approve_reservation(reservation)
    get_customer.make_creditcard_payment(
        reservation, "1234123412341234", "123", "12/30"
    )

    get_customer.pickup_vehicle(
        reservation_id=reservation.id,
        pickup_token="token-5",
        odometer=12500.0,
        fuel_level=0.8,
        clock=fake_clock,
    )

    fake_clock.advance(days=3)

    charges = get_customer.return_vehicle(
        reservation_id=reservation.id,
        odometer=13100.0,
        fuel_level=0.8,
        manual_damage_charge=250.0,  # Agent adds damage fee
        clock=fake_clock,
    )

    assert charges.damage_fee == 250.0


def test_idempotent_pickup(
    get_customer,
    get_main_branch,
    get_active_agent,
    get_economy_vehicle,
    get_basic_insurance_tier,
    get_pickup_and_return_dates,
    fake_clock,
):
    """Test that duplicate pickup with same token returns existing rental"""
    pickup_date, return_date = get_pickup_and_return_dates

    reservation = get_customer.create_reservation(
        vehicle=get_economy_vehicle,
        insurance_tier=get_basic_insurance_tier,
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
        clock=fake_clock,
    )

    get_active_agent.approve_reservation(reservation)
    get_customer.make_creditcard_payment(
        reservation, "1234123412341234", "123", "12/30"
    )

    # First pickup
    rental1 = get_customer.pickup_vehicle(
        reservation_id=reservation.id,
        pickup_token="same-token",
        odometer=12500.0,
        fuel_level=0.8,
        clock=fake_clock,
    )

    # Duplicate pickup with same token
    rental2 = get_customer.pickup_vehicle(
        reservation_id=reservation.id,
        pickup_token="same-token",  # Same token
        odometer=12500.0,
        fuel_level=0.8,
        clock=fake_clock,
    )

    assert rental1.id == rental2.id, "Same rental returned for duplicate pickup"
    assert len(get_customer.rentals) == 1, "Only one rental created"
