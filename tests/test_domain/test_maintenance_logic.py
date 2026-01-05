"""
Test maintenance logic.
This module contains unit tests for the maintenance logic and here is the flow:
    1. Agent creates a maintenance record but vehicle is still available for reservation.
    2. Manager approves the maintenance request and vehicle becomes out of service.
    3. User tries to reserve the vehicle after maintenance but fails due to vehicle status change.

Author: Peyman Khodabandehlouei
Date: 04-12-2025
"""

import pytest

from schemas.domain import VehicleStatus
from core import VehicleNotAvailableError


def test_maintenance_logic_and_edge_cases(
    get_suv_vehicle,
    get_main_branch,
    get_active_agent,
    get_active_manager,
    get_customer,
    get_basic_insurance_tier,
    get_pickup_and_return_dates,
):
    # Check vehicle status before maintenance
    assert get_suv_vehicle.status == VehicleStatus.AVAILABLE.value

    # Create a maintenance request
    get_active_agent.create_maintenance_request(
        vehicle=get_suv_vehicle, note="Needs maintenance"
    )

    # Check vehicle's maintenance records
    assert len(get_suv_vehicle.maintenance_records) == 1
    assert get_suv_vehicle.status == VehicleStatus.AVAILABLE.value

    # Approve the maintenance request
    get_active_manager.approve_maintenance(get_suv_vehicle.maintenance_records[-1])
    assert get_suv_vehicle.status == VehicleStatus.OUT_OF_SERVICE.value

    # Test reserving vehicle after maintenance by customer
    pickup_date, return_date = get_pickup_and_return_dates

    # Create reservation
    with pytest.raises(VehicleNotAvailableError):
        get_customer.create_reservation(
            vehicle=get_suv_vehicle,
            insurance_tier=get_basic_insurance_tier,
            add_ons=[],
            pickup_branch=get_main_branch,
            return_branch=get_main_branch,
            pickup_date=pickup_date,
            return_date=return_date,
        )
