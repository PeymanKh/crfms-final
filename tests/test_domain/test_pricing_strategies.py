"""
Test pricing strategies

This module contains unit tests for the pricing logic.
Here is a list of the available tests:
    1. First order pricing strategy which gives 15% discount on the first order.
    2. Loyalty pricing strategy which gives 10% discount on every 5th order.
    3. Normal pricing strategy which gives no discount on the first order.
    4. Parametrized test that verifies first-order, normal, and loyalty pricing with different real-world scenarios.

Author: Peyman Khodabandehlouei
Date: 02-12-2025
"""

import pytest
from datetime import date, timedelta


def test_first_order_pricing_strategy_calculations(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    """Tests first order pricing logic with 15% discount on the first order."""
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Create reservation
    reservation = get_customer.create_reservation(
        vehicle=get_compact_vehicle,
        insurance_tier=get_premium_insurance_tier,
        add_ons=[get_gps_addon],
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    # Manually calculate total price
    rental_days = (return_date - pickup_date).days

    vehicle_daily_rate = get_compact_vehicle.price_per_day
    insurance_daily_rate = get_premium_insurance_tier.price_per_day
    add_on_daily_rate = get_gps_addon.price_per_day

    # Calculate subtotal
    subtotal = (
        vehicle_daily_rate + insurance_daily_rate + add_on_daily_rate
    ) * rental_days

    # Apply 15% discount
    discount = subtotal * 0.15
    total_price = subtotal - discount

    assert rental_days == 3
    assert reservation.total_price == total_price


def test_loyalty_pricing_strategy_calculations(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    """Tests loyalty pricing logic with 10% discount on every 5th order."""
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Create 4 reservations and make the car available for another reservation
    for _ in range(4):
        # Reserve the car
        get_customer.create_reservation(
            vehicle=get_compact_vehicle,
            insurance_tier=get_premium_insurance_tier,
            add_ons=[get_gps_addon],
            pickup_branch=get_main_branch,
            return_branch=get_main_branch,
            pickup_date=pickup_date,
            return_date=return_date,
        )

        # Update the status
        get_compact_vehicle.make_available()

    # Reserve the car for 5th time
    get_customer.create_reservation(
        vehicle=get_compact_vehicle,
        insurance_tier=get_premium_insurance_tier,
        add_ons=[get_gps_addon],
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    # Manually calculate total price
    rental_days = (return_date - pickup_date).days

    vehicle_daily_rate = get_compact_vehicle.price_per_day
    insurance_daily_rate = get_premium_insurance_tier.price_per_day
    add_on_daily_rate = get_gps_addon.price_per_day

    # Calculate subtotal
    subtotal = (
        vehicle_daily_rate + insurance_daily_rate + add_on_daily_rate
    ) * rental_days

    # Apply 15% discount
    discount = subtotal * 0.10
    total_price = subtotal - discount

    # Access the last reservation
    last_reservation = get_customer.reservations[-1]

    assert last_reservation.total_price == total_price


def test_normal_pricing_strategy_calculations(
    get_customer,
    get_main_branch,
    get_compact_vehicle,
    get_economy_vehicle,
    get_gps_addon,
    get_premium_insurance_tier,
    get_pickup_and_return_dates,
):
    """Tests normal pricing logic with no discount on normal orders."""
    # Get pickup and return dates
    pickup_date, return_date = get_pickup_and_return_dates

    # Create reservation 1
    get_customer.create_reservation(
        vehicle=get_economy_vehicle,
        insurance_tier=get_premium_insurance_tier,
        add_ons=[get_gps_addon],
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    # Create reservation 2
    reservation = get_customer.create_reservation(
        vehicle=get_compact_vehicle,
        insurance_tier=get_premium_insurance_tier,
        add_ons=[get_gps_addon],
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    # Manually calculate total price
    rental_days = (return_date - pickup_date).days

    vehicle_daily_rate = get_compact_vehicle.price_per_day
    insurance_daily_rate = get_premium_insurance_tier.price_per_day
    add_on_daily_rate = get_gps_addon.price_per_day

    # Calculate subtotal
    total_price = (
        vehicle_daily_rate + insurance_daily_rate + add_on_daily_rate
    ) * rental_days

    assert reservation.total_price == total_price


@pytest.mark.parametrize(
    "vehicle_fixture, insurance_fixture, addon_fixtures, rental_days, "
    "reservations_before, discount_rate",
    [
        ("get_economy_vehicle", "get_basic_insurance_tier", [], 1, 0, 0.15),
        (
            "get_compact_vehicle",
            "get_premium_insurance_tier",
            ["get_gps_addon"],
            3,
            1,
            0.0,
        ),
        (
            "get_suv_vehicle",
            "get_standard_insurance_tier",
            ["get_gps_addon", "get_gps_addon"],
            7,
            4,
            0.10,
        ),
    ],
)
def test_parametrized_pricing_strategies(
    request,
    get_customer,
    get_main_branch,
    vehicle_fixture,
    insurance_fixture,
    addon_fixtures,
    rental_days,
    reservations_before,
    discount_rate,
):
    """
    Parametrized test that verifies first-order, normal, and loyalty
    pricing by varying how many reservations the customer already has.
    """
    vehicle = request.getfixturevalue(vehicle_fixture)
    insurance = request.getfixturevalue(insurance_fixture)
    addons = [request.getfixturevalue(name) for name in addon_fixtures]

    # Common pickup/return logic
    pickup_date = date.today() + timedelta(days=1)
    return_date = pickup_date + timedelta(days=rental_days)

    # Create N prior reservations to set up the correct strategy
    for _ in range(reservations_before):
        get_customer.create_reservation(
            vehicle=vehicle,
            insurance_tier=insurance,
            add_ons=addons,
            pickup_branch=get_main_branch,
            return_branch=get_main_branch,
            pickup_date=pickup_date,
            return_date=return_date,
        )
        # Make vehicle available again
        vehicle.make_available()

    # This is the reservation we actually assert on
    reservation = get_customer.create_reservation(
        vehicle=vehicle,
        insurance_tier=insurance,
        add_ons=addons,
        pickup_branch=get_main_branch,
        return_branch=get_main_branch,
        pickup_date=pickup_date,
        return_date=return_date,
    )

    # Manual expected price
    vehicle_daily = vehicle.price_per_day
    insurance_daily = insurance.price_per_day
    addons_daily = sum(add_on.price_per_day for add_on in addons)

    subtotal = (vehicle_daily + insurance_daily + addons_daily) * rental_days
    expected_total = subtotal * (1 - discount_rate)

    assert reservation.total_price == pytest.approx(expected_total)
