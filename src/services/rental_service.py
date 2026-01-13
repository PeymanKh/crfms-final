"""
Rental Service

Handles rental management operations including pickup, return, and extension logic.
Orchestrates business rules for vehicle rental lifecycle.

Author: Peyman Khodabandehlouei
Date: 13-01-2026
"""

import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from core.database_manager import db_manager
from core.clock_service import SystemClock
from schemas.db_models import (
    RentalDocument,
    RentalReadingDocument,
    RentalChargesDocument,
)
from schemas.api.requests import (
    PickupVehicleRequest,
    ReturnVehicleRequest,
    ExtendRentalRequest,
    RentalFilterRequest,
)
from schemas.api.responses import (
    RentalData,
    RentalListData,
    RentalReadingData,
    RentalChargesData,
    PickupSuccessData,
    ReturnSuccessData,
)
from schemas.domain import RentalStatus, ReservationStatus

# Business rule constants
LATE_FEE_PER_HOUR = 10.0
DAILY_KM_ALLOWANCE = 200.0
OVERAGE_PER_KM = 0.5
FUEL_REFILL_RATE = 50.0
GRACE_PERIOD_HOURS = 1

# Logger
logger = logging.getLogger(__name__)


class RentalService:
    """
    Service for rental management operations.

    Handles business logic for vehicle pickup, return, extension, and queries.
    Orchestrates interactions between domain entities, database, and external services.
    """

    def __init__(self, clock=None):
        """
        Initialize rental service with optional clock injection.

        Args:
            clock: ClockService instance (defaults to SystemClock for production)
        """
        self._clock = clock or SystemClock()

    async def pickup_vehicle(self, request: PickupVehicleRequest) -> PickupSuccessData:
        """
        Process vehicle pickup operation (idempotent).

        Business Rules:
            1. Check if rental already exists with this pickup_token (idempotency)
            2. Validate reservation exists and is in 'approved' status
            3. Validate agent exists
            4. Check vehicle is not maintenance-due
            5. Create rental with initial readings
            6. Update reservation status to 'completed' (pickup happened)

        Args:
            request (PickupVehicleRequest): Validated pickup request data

        Returns:
            PickupSuccessData: Created/existing rental with success message

        Raises:
            ValueError: If validation fails (reservation not found, wrong status, maintenance due, etc.)
        """
        # Check idempotency, if rental with this token exists, return it
        existing_rental = await db_manager.find_rental_by_pickup_token(
            request.pickup_token
        )

        if existing_rental:
            logger.info(
                f"Idempotent pickup detected: pickup_token '{request.pickup_token}' "
                f"already used for rental {existing_rental['_id']}"
            )
            # Return existing rental (idempotent response)
            rental_data = await self._convert_rental_doc_to_response(existing_rental)
            return PickupSuccessData(
                rental=rental_data,
                message="Vehicle already picked up (idempotent operation)",
            )

        # Validate reservation exists and get details
        reservation_doc = await db_manager.find_reservation_by_id(
            request.reservation_id
        )
        if not reservation_doc:
            raise ValueError(
                f"Reservation with ID '{request.reservation_id}' not found"
            )

        # Validate reservation status
        if reservation_doc["status"] != ReservationStatus.APPROVED.value:
            raise ValueError(
                f"Reservation must be in 'approved' status for pickup. "
                f"Current status: '{reservation_doc['status']}'"
            )

        # Check if reservation already has a rental
        existing_rental_for_reservation = await db_manager.find_rental_by_reservation(
            request.reservation_id
        )
        if existing_rental_for_reservation:
            raise ValueError(
                f"Reservation '{request.reservation_id}' has already been picked up. "
                f"Rental ID: {existing_rental_for_reservation['_id']}"
            )

        # Validate agent exists
        agent_doc = await db_manager.find_employee_by_id(request.agent_id)
        if not agent_doc:
            raise ValueError(f"Agent with ID '{request.agent_id}' not found")

        # Validate vehicle exists and get details
        vehicle_id = reservation_doc["vehicle_id"]
        vehicle_doc = await db_manager.find_vehicle_by_id(vehicle_id)
        if not vehicle_doc:
            raise ValueError(f"Vehicle with ID '{vehicle_id}' not found")

        # Check vehicle maintenance status
        if vehicle_doc.get("status") == "maintenance_due":
            raise ValueError(
                f"Vehicle '{vehicle_id}' is due for maintenance and cannot be picked up"
            )

        # Determine pickup timestamp
        pickup_timestamp = request.pickup_timestamp or self._clock.now()

        # Create rental readings document
        pickup_readings_doc = RentalReadingDocument(
            odometer=request.odometer_reading,
            fuel_level=request.fuel_level,
            timestamp=pickup_timestamp,
        )

        # Generate rental ID
        rental_id = str(uuid.uuid4())
        current_time = self._clock.now()

        # Create rental document
        rental_doc = RentalDocument(
            _id=rental_id,
            status=RentalStatus.ACTIVE.value,
            reservation_id=request.reservation_id,
            vehicle_id=vehicle_id,
            customer_id=reservation_doc["customer_id"],
            agent_id=request.agent_id,
            pickup_token=request.pickup_token,
            pickup_readings=pickup_readings_doc,
            return_readings=None,
            charges=None,
            created_at=current_time,
            updated_at=current_time,
        )

        # Save rental to the database
        try:
            await db_manager.create_rental(rental_doc)
            logger.info(f"Successfully created rental: {rental_id}")
        except Exception as e:
            logger.error(f"Failed to create rental: {e}")
            raise

        # Update reservation status to 'completed' (pickup happened)
        try:
            await db_manager.update_reservation(
                request.reservation_id, {"status": ReservationStatus.COMPLETED.value}
            )
            logger.info(
                f"Updated reservation {request.reservation_id} status to 'completed'"
            )
        except Exception as e:
            logger.error(f"Failed to update reservation status: {e}")
            # Note: Rental is created but reservation status update failed
            # In production, you might want to use a transaction or saga pattern

        # Update vehicle status to 'picked_up'
        try:
            await db_manager.update_vehicle(request.vehicle_id, {"status": "picked_up"})
            logger.info(f"Updated vehicle {request.vehicle_id} status to 'picked_up'")
        except Exception as e:
            logger.error(f"Failed to update vehicle status: {e}")

        # Convert to response model
        rental_data = await self._convert_rental_doc_to_response(
            rental_doc.model_dump(by_alias=True)
        )

        return PickupSuccessData(
            rental=rental_data, message="Vehicle picked up successfully"
        )

    async def return_vehicle(
        self, rental_id: str, request: ReturnVehicleRequest
    ) -> ReturnSuccessData:
        """
        Process vehicle return operation with charge calculation.

        Business Rules:
            1. Rental must exist and be in 'active' status
            2. Agent must exist
            3. Odometer must be >= pickup odometer
            4. Grace period: 1 hour free after due time
            5. Late fee: $10/hour after grace period (rounded up)
            6. Mileage allowance: 200 km/day
            7. Mileage overage: $0.50/km over allowance
            8. Fuel refill: $50/full tank (proportional if lower than pickup)
            9. Damage charge: Optional manual assessment

        Args:
            rental_id (str): Rental ID to complete
            request (ReturnVehicleRequest): Validated return request data

        Returns:
            ReturnSuccessData: Updated rental with calculated charges

        Raises:
            ValueError: If validation fails or rental already returned
        """
        # Validate rental exists
        rental_doc = await db_manager.find_rental_by_id(rental_id)
        if not rental_doc:
            raise ValueError(f"Rental with ID '{rental_id}' not found")

        # Validate rental status
        if rental_doc["status"] != RentalStatus.ACTIVE.value:
            raise ValueError(
                f"Rental must be in 'active' status for return. "
                f"Current status: '{rental_doc['status']}'"
            )

        # Validate agent exists
        agent_doc = await db_manager.find_employee_by_id(request.agent_id)
        if not agent_doc:
            raise ValueError(f"Agent with ID '{request.agent_id}' not found")

        # Get associated reservation for due date calculation
        reservation_doc = await db_manager.find_reservation_by_id(
            rental_doc["reservation_id"]
        )
        if not reservation_doc:
            raise ValueError(
                f"Associated reservation '{rental_doc['reservation_id']}' not found"
            )

        # Validate odometer reading
        pickup_odometer = rental_doc["pickup_readings"]["odometer"]
        if request.odometer_reading < pickup_odometer:
            raise ValueError(
                f"Return odometer ({request.odometer_reading} km) cannot be less than "
                f"pickup odometer ({pickup_odometer} km)"
            )

        # Determine return timestamp
        return_timestamp = request.return_timestamp or self._clock.now()

        # Calculate charges using business rules
        charges = self._calculate_rental_charges(
            rental_doc=rental_doc,
            reservation_doc=reservation_doc,
            return_odometer=request.odometer_reading,
            return_fuel_level=request.fuel_level,
            return_timestamp=return_timestamp,
            manual_damage_charge=request.damage_charge or 0.0,
        )

        # Create return readings document
        return_readings_doc = RentalReadingDocument(
            odometer=request.odometer_reading,
            fuel_level=request.fuel_level,
            timestamp=return_timestamp,
        )

        # Update rental with return data
        update_data = {
            "status": RentalStatus.COMPLETED.value,
            "return_readings": return_readings_doc.model_dump(),
            "charges": charges.model_dump(),
            "updated_at": self._clock.now(),
        }

        try:
            success = await db_manager.update_rental(rental_id, update_data)
            if not success:
                raise ValueError(f"Failed to update rental {rental_id}")

            logger.info(
                f"Successfully completed rental {rental_id}. "
                f"Total charges: ${charges.total:.2f}"
            )
        except Exception as e:
            logger.error(f"Failed to update rental: {e}")
            raise

        # Update vehicle status to 'available'
        try:
            await db_manager.update_vehicle(request.vehicle_id, {"status": "available"})
            logger.info(f"Updated vehicle {request.vehicle_id} status to 'available'")
        except Exception as e:
            logger.error(f"Failed to update vehicle status: {e}")

        # Get updated rental
        updated_rental_doc = await db_manager.find_rental_by_id(rental_id)
        rental_data = await self._convert_rental_doc_to_response(updated_rental_doc)

        return ReturnSuccessData(
            rental=rental_data,
            message=f"Vehicle returned successfully. Total charges: ${charges.total:.2f}",
        )

    async def extend_rental(
        self, rental_id: str, request: ExtendRentalRequest
    ) -> RentalData:
        """
        Extend an active rental to a new return date.

        Validates no conflicting reservations exist for the vehicle during
        the extension period.

        Business Rules:
        1. Rental must be in 'active' status
        2. new_return_date must be after current return_date
        3. Vehicle must not have conflicting reservation during extension
        4. Update associated reservation's return_date
        5. Recalculate reservation price for extended period

        Args:
            rental_id (str): Rental ID to extend
            request (ExtendRentalRequest): New return date

        Returns:
            RentalData: Updated rental information

        Raises:
            ValueError: If validation fails or conflicts exist
        """
        # Step 1: Validate rental exists and is active
        rental_doc = await db_manager.find_rental_by_id(rental_id)
        if not rental_doc:
            raise ValueError(f"Rental with ID '{rental_id}' not found")

        if rental_doc["status"] != RentalStatus.ACTIVE.value:
            raise ValueError(
                f"Can only extend active rentals. Current status: '{rental_doc['status']}'"
            )

        # Step 2: Get associated reservation
        reservation_doc = await db_manager.find_reservation_by_id(
            rental_doc["reservation_id"]
        )
        if not reservation_doc:
            raise ValueError(
                f"Associated reservation '{rental_doc['reservation_id']}' not found"
            )

        # FIX: Convert MongoDB date to date object for comparison
        from datetime import datetime as dt, date

        current_return_date = reservation_doc["return_date"]
        if isinstance(current_return_date, str):
            current_return_date = dt.fromisoformat(current_return_date).date()
        elif isinstance(current_return_date, dt):
            current_return_date = current_return_date.date()
        elif not isinstance(current_return_date, date):
            raise ValueError(f"Invalid return_date type: {type(current_return_date)}")

        # Step 3: Validate new return date is after current
        if request.new_return_date <= current_return_date:
            raise ValueError(
                f"new_return_date ({request.new_return_date}) must be after "
                f"current return date ({current_return_date})"
            )

        # Step 4: Check for conflicts with other reservations
        vehicle_id = rental_doc["vehicle_id"]
        has_conflict = not await db_manager.check_rental_extension_conflict(
            vehicle_id=vehicle_id,
            current_return_date=current_return_date,
            new_return_date=request.new_return_date,
            exclude_reservation_id=rental_doc["reservation_id"],
        )

        if has_conflict:
            raise ValueError(
                f"Cannot extend rental: Vehicle '{vehicle_id}' has conflicting "
                f"reservation between {current_return_date} and {request.new_return_date}"
            )

        # Step 5: Update reservation return date
        try:
            await db_manager.update_reservation(
                rental_doc["reservation_id"], {"return_date": request.new_return_date}
            )
            logger.info(
                f"Extended rental {rental_id}: "
                f"{current_return_date} -> {request.new_return_date}"
            )
        except Exception as e:
            logger.error(f"Failed to extend rental: {e}")
            raise

        # Step 6: Get updated rental
        updated_rental_doc = await db_manager.find_rental_by_id(rental_id)
        return await self._convert_rental_doc_to_response(updated_rental_doc)

    async def get_rental_by_id(self, rental_id: str) -> Optional[RentalData]:
        """
        Get rental by ID.

        Args:
            rental_id (str): Rental's unique identifier

        Returns:
            Optional[RentalData]: Rental data or None if not found
        """
        rental_doc = await db_manager.find_rental_by_id(rental_id)

        if not rental_doc:
            logger.info(f"Rental not found: {rental_id}")
            return None

        return await self._convert_rental_doc_to_response(rental_doc)

    async def list_rentals(self, filters: RentalFilterRequest) -> RentalListData:
        """
        List rentals with optional filters.

        Args:
            filters (RentalFilterRequest): Filter criteria

        Returns:
            RentalListData: List of rentals and total count
        """
        # Build MongoDB query filters
        query_filters: Dict[str, Any] = {}

        if filters.customer_id is not None:
            query_filters["customer_id"] = filters.customer_id

        if filters.vehicle_id is not None:
            query_filters["vehicle_id"] = filters.vehicle_id

        if filters.agent_id is not None:
            query_filters["agent_id"] = filters.agent_id

        if filters.status is not None:
            query_filters["status"] = filters.status

        if filters.reservation_id is not None:
            query_filters["reservation_id"] = filters.reservation_id

        # Query database
        rental_docs = await db_manager.find_rentals(query_filters)

        # Convert to response models
        rentals = [
            await self._convert_rental_doc_to_response(doc) for doc in rental_docs
        ]

        logger.info(f"Retrieved {len(rentals)} rentals with filters: {query_filters}")

        return RentalListData(rentals=rentals, total_count=len(rentals))

    def _calculate_rental_charges(
        self,
        rental_doc: Dict[str, Any],
        reservation_doc: Dict[str, Any],
        return_odometer: float,
        return_fuel_level: float,
        return_timestamp: datetime,
        manual_damage_charge: float,
    ) -> RentalChargesDocument:
        """
        Calculate all rental charges according to business rules.

        Business Rules (from domain/rental/rental.py):
        1. Grace period: 1 hour after due time (no late fee)
        2. Late fee: $10/hour after grace period (rounded up to next hour)
        3. Mileage allowance: 200 km/day
        4. Mileage overage: $0.50/km over allowance
        5. Fuel refill: $50/full tank (proportional if lower than pickup)
        6. Damage fee: Manual assessment by agent

        Args:
            rental_doc: Rental document from database
            reservation_doc: Associated reservation document
            return_odometer: Odometer reading at return
            return_fuel_level: Fuel level at return
            return_timestamp: When vehicle was returned
            manual_damage_charge: Optional damage assessment

        Returns:
            RentalChargesDocument: Itemized charges with total
        """
        import math
        from datetime import timedelta, datetime as dt

        # Get pickup data
        pickup_readings = rental_doc["pickup_readings"]
        pickup_odometer = pickup_readings["odometer"]
        pickup_fuel_level = pickup_readings["fuel_level"]
        pickup_timestamp = pickup_readings["timestamp"]

        if isinstance(pickup_timestamp, str):
            pickup_timestamp = dt.fromisoformat(pickup_timestamp)

        # Get reservation dates for due time calculation
        pickup_date = reservation_doc["pickup_date"]
        return_date = reservation_doc["return_date"]

        # Convert to date objects if they're strings
        if isinstance(pickup_date, str):
            pickup_date = dt.fromisoformat(pickup_date).date()
        elif isinstance(pickup_date, dt):
            pickup_date = pickup_date.date()

        if isinstance(return_date, str):
            return_date = dt.fromisoformat(return_date).date()
        elif isinstance(return_date, dt):
            return_date = return_date.date()

        # Calculate rental days
        rental_days = (return_date - pickup_date).days
        if rental_days == 0:
            rental_days = 1  # Minimum 1 day

        # Calculate due datetime (end of return date)
        due_datetime = pickup_timestamp + timedelta(days=rental_days)

        # Calculate grace period end (1 hour after due time)
        grace_end_datetime = due_datetime + timedelta(hours=GRACE_PERIOD_HOURS)

        # === Late Fee Calculation ===
        late_fee = 0.0
        if return_timestamp > grace_end_datetime:
            late_seconds = (return_timestamp - grace_end_datetime).total_seconds()
            late_hours = math.ceil(late_seconds / 3600)  # Round up to next hour
            late_fee = late_hours * LATE_FEE_PER_HOUR
            logger.info(
                f"Late return detected: {late_hours} hours late, "
                f"fee: ${late_fee:.2f}"
            )

        # === Mileage Overage Calculation ===
        allowed_km = rental_days * DAILY_KM_ALLOWANCE
        actual_km = return_odometer - pickup_odometer
        overage_km = max(0, actual_km - allowed_km)
        mileage_overage_fee = overage_km * OVERAGE_PER_KM

        logger.info(
            f"Mileage: {actual_km:.1f} km driven, "
            f"{allowed_km:.1f} km allowed, "
            f"{overage_km:.1f} km overage, "
            f"fee: ${mileage_overage_fee:.2f}"
        )

        # === Fuel Refill Calculation ===
        fuel_difference = pickup_fuel_level - return_fuel_level
        fuel_refill_fee = max(0, fuel_difference * FUEL_REFILL_RATE)

        logger.info(
            f"Fuel: {pickup_fuel_level:.2f} at pickup, "
            f"{return_fuel_level:.2f} at return, "
            f"difference: {fuel_difference:.2f}, "
            f"fee: ${fuel_refill_fee:.2f}"
        )

        # === Base Price ===
        base_price = reservation_doc["total_price"]

        # Create charges document
        return RentalChargesDocument(
            base_price=base_price,
            late_fee=late_fee,
            mileage_overage_fee=mileage_overage_fee,
            fuel_refill_fee=fuel_refill_fee,
            damage_fee=manual_damage_charge,
        )

    async def _convert_rental_doc_to_response(
        self, rental_doc: Dict[str, Any]
    ) -> RentalData:
        """
        Convert MongoDB rental document to API response model.

        Args:
            rental_doc: Rental document from database

        Returns:
            RentalData: Response model for API
        """
        # Convert pickup readings
        pickup_readings = RentalReadingData(
            odometer=rental_doc["pickup_readings"]["odometer"],
            fuel_level=rental_doc["pickup_readings"]["fuel_level"],
            timestamp=rental_doc["pickup_readings"]["timestamp"],
        )

        # Convert return readings (if exists)
        return_readings = None
        if rental_doc.get("return_readings"):
            return_readings = RentalReadingData(
                odometer=rental_doc["return_readings"]["odometer"],
                fuel_level=rental_doc["return_readings"]["fuel_level"],
                timestamp=rental_doc["return_readings"]["timestamp"],
            )

        # Convert charges (if exists)
        charges = None
        if rental_doc.get("charges"):
            charges = RentalChargesData(
                base_price=rental_doc["charges"]["base_price"],
                late_fee=rental_doc["charges"]["late_fee"],
                mileage_overage_fee=rental_doc["charges"]["mileage_overage_fee"],
                fuel_refill_fee=rental_doc["charges"]["fuel_refill_fee"],
                damage_fee=rental_doc["charges"]["damage_fee"],
            )

        return RentalData(
            id=rental_doc["_id"],
            status=rental_doc["status"],
            reservation_id=rental_doc["reservation_id"],
            vehicle_id=rental_doc["vehicle_id"],
            customer_id=rental_doc["customer_id"],
            agent_id=rental_doc["agent_id"],
            pickup_token=rental_doc["pickup_token"],
            pickup_readings=pickup_readings,
            return_readings=return_readings,
            charges=charges,
            created_at=rental_doc["created_at"],
            updated_at=rental_doc["updated_at"],
        )


# Singleton instance
rental_service = RentalService()
