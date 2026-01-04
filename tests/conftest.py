"""
Fixed instances for testing

This module defines reusable pytest fixtures that provide ready to use objects for testing.
Here is a list of the available fixtures:
- Branch and users:
    - get_main_branch: Returns a main Branch instance.
    - get_customer: Returns a sample Customer.
    - get_active_agent: Returns an active Agent assigned to the main branch.
    - get_active_manager: Returns an active Manager assigned to the main branch.

- Vehicle classes:
    - get_economy_vehicle_class: Economy class with low base daily rate and basic features.
    - get_compact_vehicle_class: Compact class with moderate base daily rate and comfort features.
    - get_suv_vehicle_class: SUV class with higher base daily rate and family-oriented features.

- Vehicles:
    - get_economy_vehicle: Sample vehicle with economy class.
    - get_compact_vehicle: Sample vehicle with compact class.
    - get_suv_vehicle: Sample vehicle with SUV class.

- Reservations:
    - get_reservation: Returns a sample Reservation instance.

- Add-ons:
    - get_gps_addon: GPS navigation add-on.
    - get_child_seat_addon: Child seat add-on for traveling with toddlers.

- Insurance tiers:
    - get_basic_insurance_tier: Basic insurance coverage with minimal protection.
    - get_standard_insurance_tier: Standard insurance coverage including collision.
    - get_premium_insurance_tier: Premium insurance coverage with extended protection.

- Payments:
    - get_credit_card_payment_creator: Returns a preconfigured CreditCardPaymentCreator.
    - get_paypal_payment_creator: Returns a preconfigured PaypalPaymentCreator.

- Notifications:
    - get_notification_manager: Returns a ConcreteNotificationManager instance.
    - get_customer_notification_subscriber: Returns a CustomerSubscriber instance.
    - get_agent_notification_subscriber: Returns an AgentSubscriber instance.

- Clock
    - get_pickup_and_return_dates: Returns a tuple of pickup and return dates for testing.

Author: Peyman Khodabandehlouei
Date: 01-12-2025
"""

import pytest
from datetime import date, datetime, timedelta

from entities.branch import Branch
from entities.user import Agent, Manager, Customer
from entities.vehicle import Vehicle, VehicleClass
from entities.reservation import AddOn, InsuranceTier
from entities.payment import CreditCardPaymentCreator, PaypalPaymentCreator
from entities.notification import ConcreteNotificationManager, AgentSubscriber, CustomerSubscriber

from schemas.entities import Gender, EmploymentType, VehicleStatus


@pytest.fixture
def get_main_branch() -> Branch:
    """
    Returns a Branch instance with the following properties:
        1. Name: Main branch
        2. City: Istanbul
        3. Address: Kaġithane merkez
        4. Phone number: +905343940796
    """
    return Branch(
        name="Main branch",
        city="Istanbul",
        address="Kaġithane merkez",
        phone_number="+905343940796",
    )


@pytest.fixture
def get_customer() -> Customer:
    """
    Returns a Customer instance with the following properties:
        1. First name: Peyman
        2. Last name: Khodabandehlouei
        3. Gender: Male
        4. Birthdate: 1995-01-01
        5. Email: itspeey@gmail.com
        6. Address: Beşiktaş
        7. Phone number: +905343940796
    """
    return Customer(
        first_name="Peyman",
        last_name="Khodabandehlouei",
        gender=Gender.MALE,
        birth_date=date(1995, 1, 1),
        email="itspeey@gmai.com",
        address="Beşiktaş",
        phone_number="+905343940796",
    )


@pytest.fixture
def get_active_agent(get_main_branch) -> Agent:
    """
    Returns an Agent instance with the following properties:
        1. First name: Buse
        2. Last name: Yilmaz
        3. Gender: Female
        4. Birthdate: 1990-01-01
        5. Email: buse.yilmaz@business.com
        6. Address: Kadiköy
        7. Phone number: +905343940796
        8. Branch: Branch("Main branch")
        9. Is active: True
        10. Salary: 20_000
        11. Hire date: 2015-01-01
        12. Employment type: Full time
    """
    return Agent(
        first_name="Buse",
        last_name="Yilmaz",
        gender=Gender.FEMALE,
        birth_date=date(1990, 1, 1),
        email="buse.yilmaz@business.com",
        address="Kadiköy",
        phone_number="905343940796",
        branch=get_main_branch,
        is_active=True,
        salary=20_000,
        hire_date=date(2015, 1, 1),
        employment_type=EmploymentType.FULL_TIME,
    )


@pytest.fixture
def get_active_manager(get_main_branch) -> Manager:
    """
    Returns a Manager instance with the following properties:
        1. First name: Ali
        2. Last name: Talha
        3. Gender: Male
        4. Birthdate: 1985-01-01
        5. Email: ali.talha@business.com
        6. Address: Kadiköy
        7. Phone number: +905343940796
        8. Branch: Branch("Main branch")
        9. Is active: True
        10. Salary: 40_000
        11. Hire date: 2010-01-01
        12. Employment type: Full time
    """
    return Manager(
        first_name="Ali",
        last_name="Talha",
        gender=Gender.MALE,
        birth_date=date(1985, 1, 1),
        email="ali.talha@business.com",
        address="Kadiköy",
        phone_number="905343940796",
        branch=get_main_branch,
        is_active=True,
        salary=40_000,
        hire_date=date(2010, 1, 1),
        employment_type=EmploymentType.FULL_TIME,
    )


@pytest.fixture
def get_economy_vehicle_class() -> VehicleClass:
    """
    Returns a VehicleClass instance with the following properties:
        1. Name: Economy
        2. Description: Small, fuel-efficient vehicles for city driving.
        3. Base daily rate: 30.0
        4. Features: ["Air conditioning", "Manual transmission"]
    """
    return VehicleClass(
        name="Economy",
        description="Small, fuel-efficient vehicles for city driving.",
        base_daily_rate=30.0,
        features=[
            "Air conditioning",
            "Manual transmission",
        ],
    )


@pytest.fixture
def get_compact_vehicle_class() -> VehicleClass:
    """
    Returns a VehicleClass instance with the following properties:
        1. Name: Compact
        2. Description: Compact cars with more space and comfort than economy class.
        3. Base daily rate: 45.0
        4. Features: ["Air conditioning", "Automatic transmission"]
    """
    return VehicleClass(
        name="Compact",
        description="Compact cars with more space and comfort than economy class.",
        base_daily_rate=45.0,
        features=[
            "Air conditioning",
            "Automatic transmission",
        ],
    )


@pytest.fixture
def get_suv_vehicle_class() -> VehicleClass:
    """
    Returns a VehicleClass instance with the following properties:
        1. Name: SUV
        2. Description: Larger vehicles suitable for families and long trips.
        3. Base daily rate: 70.0
        4. Features: ["Automatic transmission", "All-wheel drive"]
    """
    return VehicleClass(
        name="SUV",
        description="Larger vehicles suitable for families and long trips.",
        base_daily_rate=70.0,
        features=[
            "Automatic transmission",
            "All-wheel drive",
        ],
    )


@pytest.fixture
def get_economy_vehicle(get_economy_vehicle_class, get_main_branch) -> Vehicle:
    """
    Returns an Economy class Vehicle instance (Toyota Yaris) with the following properties:
        1. Vehicle class: Economy
        2. Current branch: Main branch
        3. Status: AVAILABLE
        4. Brand: Toyota
        5. Model: Yaris
        6. Color: White
        7. Licence plate: ECN-001
        8. Fuel level: 0.8
        9. Last service odometer: 10_000
        10. Odometer: 12_500
        11. Price per day: get_economy_vehicle_class.base_daily_rate + 5
        12. Maintenance records: []
    """
    return Vehicle(
        vehicle_class=get_economy_vehicle_class,
        current_branch=get_main_branch,
        status=VehicleStatus.AVAILABLE,
        brand="Toyota",
        model="Yaris",
        color="White",
        licence_plate="ECN-001",
        fuel_level=0.8,
        last_service_odometer=10_000,
        odometer=12_500,
        price_per_day=get_economy_vehicle_class.base_daily_rate + 5,
        maintenance_records=[],
    )


@pytest.fixture
def get_compact_vehicle(get_compact_vehicle_class, get_main_branch) -> Vehicle:
    """
    Returns a Compact class Vehicle instance (Volkswagen Golf) with the following properties:
        1. Vehicle class: Compact
        2. Current branch: Main branch
        3. Status: AVAILABLE
        4. Brand: Volkswagen
        5. Model: Golf
        6. Color: Gray
        7. Licence plate: CMP-001
        8. Fuel level: 0.7
        9. Last service odometer: 20_000
        10. Odometer: 22_000
        11. Price per day: get_compact_vehicle_class.base_daily_rate + 10
        12. Maintenance records: []
    """
    return Vehicle(
        vehicle_class=get_compact_vehicle_class,
        current_branch=get_main_branch,
        status=VehicleStatus.AVAILABLE,
        brand="Volkswagen",
        model="Golf",
        color="Gray",
        licence_plate="CMP-001",
        fuel_level=0.7,
        last_service_odometer=20_000,
        odometer=22_000,
        price_per_day=get_compact_vehicle_class.base_daily_rate + 10,
        maintenance_records=[],
    )


@pytest.fixture
def get_suv_vehicle(get_suv_vehicle_class, get_main_branch) -> Vehicle:
    """
    Returns an SUV class Vehicle instance (Toyota RAV4) with the following properties:
        1. Vehicle class: SUV
        2. Current branch: Main branch
        3. Status: AVAILABLE
        4. Brand: Toyota
        5. Model: RAV4
        6. Color: Black
        7. Licence plate: SUV-001
        8. Fuel level: 0.9
        9. Last service odometer: 30_000
        10. Odometer: 33_000
        11. Price per day: get_suv_vehicle_class.base_daily_rate + 20
        12. Maintenance records: []
    """
    return Vehicle(
        vehicle_class=get_suv_vehicle_class,
        current_branch=get_main_branch,
        status=VehicleStatus.AVAILABLE,
        brand="Toyota",
        model="RAV4",
        color="Black",
        licence_plate="SUV-001",
        fuel_level=0.9,
        last_service_odometer=30_000,
        odometer=33_000,
        price_per_day=get_suv_vehicle_class.base_daily_rate + 20,
        maintenance_records=[],
    )


@pytest.fixture
def get_credit_card_payment_creator() -> CreditCardPaymentCreator:
    return CreditCardPaymentCreator(
        card_number="1234 1234 1234 1234", cvv="123", expiry="12/30"
    )


@pytest.fixture
def get_paypal_payment_creator() -> PaypalPaymentCreator:
    return PaypalPaymentCreator(
        email="itspeey@gmail.com", auth_token="ABCDEFG123456789"
    )


@pytest.fixture
def get_notification_manager() -> ConcreteNotificationManager:
    return ConcreteNotificationManager()


@pytest.fixture
def get_customer_notification_subscriber() -> CustomerSubscriber:
    return CustomerSubscriber()


@pytest.fixture
def get_agent_notification_subscriber() -> AgentSubscriber:
    return AgentSubscriber()


@pytest.fixture
def get_gps_addon() -> AddOn:
    """
    Returns an AddOn instance for GPS navigation with the following properties:
        1. Name: GPS Navigation
        2. Description: In-car GPS navigation system for easier route guidance.
        3. Price per day: 5.0
    """
    return AddOn(
        name="GPS Navigation",
        description="In-car GPS navigation system for easier route guidance.",
        price_per_day=5.0,
    )


@pytest.fixture
def get_child_seat_addon() -> AddOn:
    """
    Returns an AddOn instance for Child Seat with the following properties:
        1. Name: Child Seat
        2. Description: Safety-approved child seat suitable for toddlers.
        3. Price per day: 7.5
    """
    return AddOn(
        name="Child Seat",
        description="Safety-approved child seat suitable for toddlers.",
        price_per_day=7.5,
    )


@pytest.fixture
def get_basic_insurance_tier() -> InsuranceTier:
    """
    Returns an InsuranceTier instance for Basic coverage with the following properties:
        1. Tier name: Basic
        2. Description: Basic liability coverage with minimal protection.
        3. Price per day: 5.0
    """
    return InsuranceTier(
        tier_name="Basic",
        description="Basic liability coverage with minimal protection.",
        price_per_day=5.0,
    )


@pytest.fixture
def get_standard_insurance_tier() -> InsuranceTier:
    """
    Returns an InsuranceTier instance for Standard coverage with the following properties:
        1. Tier name: Standard
        2. Description: Standard coverage including liability and collision protection.
        3. Price per day: 10.0
    """
    return InsuranceTier(
        tier_name="Standard",
        description="Standard coverage including liability and collision protection.",
        price_per_day=10.0,
    )


@pytest.fixture
def get_premium_insurance_tier() -> InsuranceTier:
    """
    Returns an InsuranceTier instance for Premium coverage with the following properties:
        1. Tier name: Premium
        2. Description: Premium coverage with extended protection and lower deductibles.
        3. Price per day: 18.0
    """
    return InsuranceTier(
        tier_name="Premium",
        description="Premium coverage with extended protection and lower deductibles.",
        price_per_day=18.0,
    )



@pytest.fixture
def get_pickup_and_return_dates(interval_days: int = 3) -> tuple[datetime, datetime]:
    pickup_date = date.today() + timedelta(days=1)
    return_date = pickup_date + timedelta(days=interval_days)
    return pickup_date, return_date
