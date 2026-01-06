"""
Reservation Service

Handles reservation management operations including CRUD logic,
price calculation, and vehicle availability validation.

Author: Peyman Khodabandehlouei
Date: 06-01-2026
"""

import uuid
import logging
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any

from core.database_manager import db_manager
from core.pricing_calculator import calculate_total_price, determine_pricing_strategy
from schemas.db_models import (
    InvoiceDocument,
    ReservationDocument,
    ReservationAddOnDocument,
)
from schemas.api.requests.reservations import (
    CreateReservationRequest,
    UpdateReservationRequest,
    ReservationFilterRequest,
)
from schemas.api.responses.reservations import (
    ReservationData,
    ReservationListData,
    ReservationAddOnData,
    InvoiceData,
)
from schemas.domain import ReservationStatus
from core.pricing_calculator import calculate_rental_days


logger = logging.getLogger(__name__)


class ReservationService:
    """
    Service for reservation management operations.

    Handles business logic for creating, reading, updating, and deleting reservations,
    including price calculation and vehicle availability validation.
    """

    @staticmethod
    async def _calculate_total_price(
        customer_id: str,
        vehicle_id: str,
        insurance_tier_id: str,
        add_on_ids: List[str],
        pickup_date: date,
        return_date: date,
    ) -> tuple[float, List[ReservationAddOnDocument], int]:
        """
        Calculate total reservation price using pricing strategy logic.

        This uses the same pricing formulas as domain model's PricingStrategy,
        ensuring consistency across the application.

        Args:
            customer_id (str): Customer ID
            vehicle_id (str): Vehicle ID
            insurance_tier_id (str): Insurance tier ID
            add_on_ids (List[str]): List of add-on IDs
            pickup_date (date): Pickup date
            return_date (date): Return date

        Returns:
            tuple[float, List[ReservationAddOnDocument], int]:
                - Total price (with discount)
                - List of add-on documents with snapshot pricing
                - Rental days

        Raises:
            ValueError: If vehicle, insurance tier, or any add-on not found
        """
        # Fetch customer (to determine pricing strategy)
        customer_doc = await db_manager.find_customer_by_id(customer_id)
        if not customer_doc:
            raise ValueError(f"Customer with ID '{customer_id}' not found")

        # Fetch vehicle
        vehicle_doc = await db_manager.find_vehicle_by_id(vehicle_id)
        if not vehicle_doc:
            raise ValueError(f"Vehicle with ID '{vehicle_id}' not found")

        # Fetch insurance tier
        insurance_doc = await db_manager.find_insurance_tier_by_id(insurance_tier_id)
        if not insurance_doc:
            raise ValueError(f"Insurance tier with ID '{insurance_tier_id}' not found")

        # Fetch add-ons
        add_on_docs = []
        add_on_documents = []
        if add_on_ids:
            add_on_docs = await db_manager.find_add_ons_by_ids(add_on_ids)

            # Validate all add-ons found
            found_ids = {doc["_id"] for doc in add_on_docs}
            missing_ids = set(add_on_ids) - found_ids
            if missing_ids:
                raise ValueError(f"Add-ons not found: {missing_ids}")

            # Create add-on documents with snapshot pricing
            add_on_documents = [
                ReservationAddOnDocument(
                    id=doc["_id"],
                    name=doc["name"],
                    price_per_day=doc["price_per_day"],
                )
                for doc in add_on_docs
            ]

        # Calculate rental days
        rental_days = calculate_rental_days(pickup_date, return_date)

        # Determine pricing strategy based on customer's reservation history
        # Count existing reservations for this customer
        existing_reservations = await db_manager.find_reservations_by_customer(
            customer_id
        )
        reservation_count = len(existing_reservations)

        strategy_type = determine_pricing_strategy(reservation_count)

        # Calculate total price using pricing calculator
        addon_prices = [doc.price_per_day for doc in add_on_documents]

        total_price = calculate_total_price(
            vehicle_price_per_day=vehicle_doc["price_per_day"],
            insurance_price_per_day=insurance_doc["price_per_day"],
            addon_prices_per_day=addon_prices,
            pickup_date=pickup_date,
            return_date=return_date,
            strategy_type=strategy_type,
        )

        logger.info(
            f"Price calculation: vehicle=${vehicle_doc['price_per_day']}/day, "
            f"insurance=${insurance_doc['price_per_day']}/day, "
            f"add-ons=${sum(addon_prices)}/day, "
            f"days={rental_days}, "
            f"strategy={strategy_type}, "
            f"customer_reservations={reservation_count}, "
            f"total=${total_price}"
        )

        return total_price, add_on_documents, rental_days

    @staticmethod
    async def create_reservation(request: CreateReservationRequest) -> ReservationData:
        """
        Create a new reservation.

        Business Rules:
        1. Validate all referenced entities exist (customer, vehicle, branches, insurance, add-ons)
        2. Check vehicle availability for the requested dates
        3. Calculate rental days and total price
        4. Create reservation with status 'pending'

        Args:
            request (CreateReservationRequest): Validated reservation creation data.

        Returns:
            ReservationData: Created reservation data for response.

        Raises:
            ValueError: If any validation fails (entity not found, vehicle unavailable)
        """
        # Validate branches exist (customer/vehicle validated in _calculate_total_price)
        pickup_branch_doc = await db_manager.find_branch_by_id(request.pickup_branch_id)
        if not pickup_branch_doc:
            raise ValueError(
                f"Pickup branch with ID '{request.pickup_branch_id}' not found"
            )

        return_branch_doc = await db_manager.find_branch_by_id(request.return_branch_id)
        if not return_branch_doc:
            raise ValueError(
                f"Return branch with ID '{request.return_branch_id}' not found"
            )

        # Check vehicle availability
        is_available = await db_manager.check_vehicle_availability(
            vehicle_id=request.vehicle_id,
            pickup_date=request.pickup_date,
            return_date=request.return_date,
        )
        if not is_available:
            raise ValueError(
                f"Vehicle '{request.vehicle_id}' is not available "
                f"from {request.pickup_date} to {request.return_date}"
            )

        # Calculate total price (validates customer, vehicle, insurance tier, and add-ons)
        total_price, add_on_documents, rental_days = (
            await ReservationService._calculate_total_price(
                customer_id=request.customer_id,
                vehicle_id=request.vehicle_id,
                insurance_tier_id=request.insurance_tier_id,
                add_on_ids=request.add_on_ids,
                pickup_date=request.pickup_date,
                return_date=request.return_date,
            )
        )

        # Generate reservation ID
        reservation_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)

        # Create invoice document
        invoice_doc = InvoiceDocument(
            id=str(uuid.uuid4()),
            status="pending",
            issued_date=current_time.date(),
            total_price=total_price,
        )

        # Create database document
        reservation_doc = ReservationDocument(
            _id=reservation_id,
            status=ReservationStatus.PENDING.value,
            customer_id=request.customer_id,
            vehicle_id=request.vehicle_id,
            insurance_tier_id=request.insurance_tier_id,
            pickup_branch_id=request.pickup_branch_id,
            return_branch_id=request.return_branch_id,
            pickup_date=request.pickup_date,
            return_date=request.return_date,
            add_ons=add_on_documents,
            total_price=total_price,
            rental_days=rental_days,
            invoice=invoice_doc,
            created_at=current_time,
            updated_at=current_time,
        )

        # Save to the database
        try:
            await db_manager.create_reservation(reservation_doc)
            logger.info(f"Successfully created reservation: {reservation_id}")
        except Exception as e:
            logger.error(f"Failed to create reservation: {e}")
            raise

        # 7. Return response data
        return ReservationData(
            id=reservation_id,
            status=ReservationStatus.PENDING.value,
            customer_id=request.customer_id,
            vehicle_id=request.vehicle_id,
            insurance_tier_id=request.insurance_tier_id,
            pickup_branch_id=request.pickup_branch_id,
            return_branch_id=request.return_branch_id,
            pickup_date=request.pickup_date,
            return_date=request.return_date,
            add_ons=[
                ReservationAddOnData(
                    id=addon.id,
                    name=addon.name,
                    price_per_day=addon.price_per_day,
                )
                for addon in add_on_documents
            ],
            total_price=total_price,
            rental_days=rental_days,
            invoice=invoice_doc,
            created_at=current_time,
            updated_at=current_time,
        )

    @staticmethod
    async def get_reservation_by_id(reservation_id: str) -> Optional[ReservationData]:
        """
        Get reservation by ID.

        Args:
            reservation_id (str): Reservation's unique identifier.

        Returns:
            Optional[ReservationData]: Reservation data or None if not found.
        """
        reservation_doc = await db_manager.find_reservation_by_id(reservation_id)

        if not reservation_doc:
            logger.info(f"Reservation not found: {reservation_id}")
            return None

        # Convert MongoDB document to response model
        return ReservationData(
            id=reservation_doc["_id"],
            status=reservation_doc["status"],
            customer_id=reservation_doc["customer_id"],
            vehicle_id=reservation_doc["vehicle_id"],
            insurance_tier_id=reservation_doc["insurance_tier_id"],
            pickup_branch_id=reservation_doc["pickup_branch_id"],
            return_branch_id=reservation_doc["return_branch_id"],
            pickup_date=reservation_doc["pickup_date"],
            return_date=reservation_doc["return_date"],
            add_ons=[
                ReservationAddOnData(
                    id=addon["id"],
                    name=addon["name"],
                    price_per_day=addon["price_per_day"],
                )
                for addon in reservation_doc.get("add_ons", [])
            ],
            total_price=reservation_doc["total_price"],
            rental_days=reservation_doc["rental_days"],
            invoice=InvoiceData(
                id=reservation_doc["invoice"]["id"],
                status=reservation_doc["invoice"]["status"],
                issued_date=reservation_doc["invoice"]["issued_date"],
                total_price=reservation_doc["invoice"]["total_price"],
            ),
            created_at=reservation_doc["created_at"],
            updated_at=reservation_doc["updated_at"],
        )

    @staticmethod
    async def update_reservation(
        reservation_id: str, request: UpdateReservationRequest
    ) -> Optional[ReservationData]:
        """
        Update reservation information.

        Business Rules:
        1. Cannot update if status is 'completed' or 'cancelled'
        2. If dates change, recalculate rental_days and total_price
        3. If vehicle changes, check availability
        4. If insurance/add-ons change, recalculate total_price
        5. Invoice price auto-syncs when reservation price changes

        Args:
            reservation_id (str): Reservation ID to update.
            request (UpdateReservationRequest): Fields to update (only non-None fields).

        Returns:
            Optional[ReservationData]: Updated reservation data or None if not found.

        Raises:
            ValueError: If validation fails or reservation cannot be updated
        """
        # Check if reservation exists
        existing_reservation = await db_manager.find_reservation_by_id(reservation_id)
        if not existing_reservation:
            logger.info(f"Reservation not found for update: {reservation_id}")
            return None

        # Validate reservation status
        current_status = existing_reservation["status"]
        if current_status in ["completed", "cancelled"]:
            raise ValueError(
                f"Cannot update reservation with status '{current_status}'"
            )

        # Build update dict
        update_data: Dict[str, Any] = {}
        needs_price_recalculation = False

        # Status update
        if request.status is not None:
            update_data["status"] = request.status.value

        # Vehicle update
        if request.vehicle_id is not None:
            vehicle_doc = await db_manager.find_vehicle_by_id(request.vehicle_id)
            if not vehicle_doc:
                raise ValueError(f"Vehicle with ID '{request.vehicle_id}' not found")

            # Check availability if vehicle changes
            pickup_date = request.pickup_date or existing_reservation["pickup_date"]
            return_date = request.return_date or existing_reservation["return_date"]

            is_available = await db_manager.check_vehicle_availability(
                vehicle_id=request.vehicle_id,
                pickup_date=pickup_date,
                return_date=return_date,
                exclude_reservation_id=reservation_id,
            )
            if not is_available:
                raise ValueError(
                    f"Vehicle '{request.vehicle_id}' is not available "
                    f"from {pickup_date} to {return_date}"
                )

            update_data["vehicle_id"] = request.vehicle_id
            needs_price_recalculation = True

        # Insurance tier update
        if request.insurance_tier_id is not None:
            insurance_doc = await db_manager.find_insurance_tier_by_id(
                request.insurance_tier_id
            )
            if not insurance_doc:
                raise ValueError(
                    f"Insurance tier with ID '{request.insurance_tier_id}' not found"
                )
            update_data["insurance_tier_id"] = request.insurance_tier_id
            needs_price_recalculation = True

        # Branch updates
        if request.pickup_branch_id is not None:
            branch_doc = await db_manager.find_branch_by_id(request.pickup_branch_id)
            if not branch_doc:
                raise ValueError(
                    f"Pickup branch with ID '{request.pickup_branch_id}' not found"
                )
            update_data["pickup_branch_id"] = request.pickup_branch_id

        if request.return_branch_id is not None:
            branch_doc = await db_manager.find_branch_by_id(request.return_branch_id)
            if not branch_doc:
                raise ValueError(
                    f"Return branch with ID '{request.return_branch_id}' not found"
                )
            update_data["return_branch_id"] = request.return_branch_id

        # Date updates
        if request.pickup_date is not None:
            update_data["pickup_date"] = request.pickup_date
            needs_price_recalculation = True

        if request.return_date is not None:
            update_data["return_date"] = request.return_date
            needs_price_recalculation = True

        # Add-ons update
        if request.add_on_ids is not None:
            needs_price_recalculation = True

        # Recalculate price if needed
        if needs_price_recalculation:
            # Get final values (updated or existing)
            final_customer_id = existing_reservation["customer_id"]
            final_vehicle_id = update_data.get(
                "vehicle_id", existing_reservation["vehicle_id"]
            )
            final_insurance_id = update_data.get(
                "insurance_tier_id", existing_reservation["insurance_tier_id"]
            )
            final_pickup_date = update_data.get(
                "pickup_date", existing_reservation["pickup_date"]
            )
            final_return_date = update_data.get(
                "return_date", existing_reservation["return_date"]
            )
            final_add_on_ids = (
                request.add_on_ids
                if request.add_on_ids is not None
                else [addon["id"] for addon in existing_reservation.get("add_ons", [])]
            )

            # Recalculate total price (includes rental_days calculation)
            total_price, add_on_documents, rental_days = (
                await ReservationService._calculate_total_price(
                    customer_id=final_customer_id,
                    vehicle_id=final_vehicle_id,
                    insurance_tier_id=final_insurance_id,
                    add_on_ids=final_add_on_ids,
                    pickup_date=final_pickup_date,
                    return_date=final_return_date,
                )
            )

            update_data["total_price"] = total_price
            update_data["rental_days"] = rental_days
            update_data["add_ons"] = [addon.model_dump() for addon in add_on_documents]

            # Auto sync invoice price
            update_data["invoice.total_price"] = total_price

            logger.info(
                f"Recalculated price for reservation {reservation_id}: ${total_price} "
                f"(invoice auto-synced)"
            )

        # If no fields to update, return current data
        if not update_data:
            logger.info(f"No fields to update for reservation: {reservation_id}")
            return await ReservationService.get_reservation_by_id(reservation_id)

        # Update in database
        try:
            success = await db_manager.update_reservation(reservation_id, update_data)
            if not success:
                return None

            logger.info(f"Successfully updated reservation: {reservation_id}")
        except Exception as e:
            logger.error(f"Failed to update reservation: {e}")
            raise

        # Return updated reservation data
        return await ReservationService.get_reservation_by_id(reservation_id)

    @staticmethod
    async def delete_reservation(reservation_id: str) -> bool:
        """
        Delete a reservation.

        Args:
            reservation_id (str): Reservation ID to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        success = await db_manager.delete_reservation(reservation_id)

        if success:
            logger.info(f"Successfully deleted reservation: {reservation_id}")
        else:
            logger.info(f"Reservation not found for deletion: {reservation_id}")

        return success

    @staticmethod
    async def list_reservations(
        filters: ReservationFilterRequest,
    ) -> ReservationListData:
        """
        List reservations with optional filters.

        Args:
            filters (ReservationFilterRequest): Filter criteria.

        Returns:
            ReservationListData: List of reservations and total count.
        """
        # Build MongoDB query filters
        query_filters: Dict[str, Any] = {}

        if filters.customer_id is not None:
            query_filters["customer_id"] = filters.customer_id

        if filters.vehicle_id is not None:
            query_filters["vehicle_id"] = filters.vehicle_id

        if filters.status is not None:
            query_filters["status"] = filters.status.value

        # Date range filter
        if filters.pickup_date_from is not None or filters.pickup_date_to is not None:
            date_filter = {}
            if filters.pickup_date_from is not None:
                date_filter["$gte"] = filters.pickup_date_from
            if filters.pickup_date_to is not None:
                date_filter["$lte"] = filters.pickup_date_to
            query_filters["pickup_date"] = date_filter

        # Query database
        reservation_docs = await db_manager.find_reservations(query_filters)

        # Convert to response models
        reservations = [
            ReservationData(
                id=doc["_id"],
                status=doc["status"],
                customer_id=doc["customer_id"],
                vehicle_id=doc["vehicle_id"],
                insurance_tier_id=doc["insurance_tier_id"],
                pickup_branch_id=doc["pickup_branch_id"],
                return_branch_id=doc["return_branch_id"],
                pickup_date=doc["pickup_date"],
                return_date=doc["return_date"],
                add_ons=[
                    ReservationAddOnData(
                        id=addon["id"],
                        name=addon["name"],
                        price_per_day=addon["price_per_day"],
                    )
                    for addon in doc.get("add_ons", [])
                ],
                total_price=doc["total_price"],
                rental_days=doc["rental_days"],
                invoice=InvoiceData(
                    id=doc["invoice"]["id"],
                    status=doc["invoice"]["status"],
                    issued_date=doc["invoice"]["issued_date"],
                    total_price=doc["invoice"]["total_price"],
                ),
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
            )
            for doc in reservation_docs
        ]

        logger.info(
            f"Retrieved {len(reservations)} reservations with filters: {query_filters}"
        )

        return ReservationListData(
            reservations=reservations, total_count=len(reservations)
        )


# Singleton instance
reservation_service = ReservationService()
