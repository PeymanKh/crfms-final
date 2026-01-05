"""
Vehicle Service

Handles vehicle management operations including CRUD and filtering logic.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

from core.database_manager import db_manager
from schemas.db_models.vehicle_models import VehicleDocument
from schemas.api.requests import (
    CreateVehicleRequest,
    UpdateVehicleRequest,
    VehicleFilterRequest,
)
from schemas.api.responses import VehicleData, VehicleListData

logger = logging.getLogger(__name__)


class VehicleService:
    """
    Service for vehicle management operations.

    Handles business logic for creating, reading, updating, and deleting vehicles.
    """

    @staticmethod
    async def create_vehicle(request: CreateVehicleRequest) -> VehicleData:
        """
        Create a new vehicle.

        Args:
            request (CreateVehicleRequest): Validated vehicle creation data.

        Returns:
            VehicleData: Created vehicle data for response.

        Raises:
            DuplicateKeyError: If plate_number already exists.
        """
        # Check if plate number already exists
        existing_vehicle = await db_manager.find_vehicle_by_plate(request.plate_number)
        if existing_vehicle:
            logger.warning(
                f"Vehicle creation attempt with duplicate plate: {request.plate_number}"
            )
            raise DuplicateKeyError(
                f"Plate number {request.plate_number} already exists"
            )

        # Generate vehicle ID
        vehicle_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)

        # Create database document
        vehicle_doc = VehicleDocument(
            _id=vehicle_id,
            plate_number=request.plate_number,
            brand=request.brand,
            model=request.model,
            year=request.year,
            vehicle_class=request.vehicle_class,
            price_per_day=request.price_per_day,
            mileage=request.mileage,
            branch_id=request.branch_id,
            status=request.status.value,
            created_at=current_time,
            updated_at=current_time,
        )

        # Save to the database
        try:
            await db_manager.create_vehicle(vehicle_doc)
            logger.info(f"Successfully created vehicle: {vehicle_id}")
        except DuplicateKeyError:
            logger.error(f"Duplicate key error for plate: {request.plate_number}")
            raise

        # Return response data
        return VehicleData(
            id=vehicle_id,
            plate_number=request.plate_number,
            brand=request.brand,
            model=request.model,
            year=request.year,
            vehicle_class=request.vehicle_class,
            price_per_day=request.price_per_day,
            mileage=request.mileage,
            branch_id=request.branch_id,
            status=request.status.value,
            created_at=current_time,
            updated_at=current_time,
        )

    @staticmethod
    async def get_vehicle_by_id(vehicle_id: str) -> Optional[VehicleData]:
        """
        Get vehicle by ID.

        Args:
            vehicle_id (str): Vehicle's unique identifier.

        Returns:
            Optional[VehicleData]: Vehicle data or None if not found.
        """
        vehicle_doc = await db_manager.find_vehicle_by_id(vehicle_id)

        if not vehicle_doc:
            logger.info(f"Vehicle not found: {vehicle_id}")
            return None

        # Convert MongoDB document to response model
        return VehicleData(
            id=vehicle_doc["_id"],
            plate_number=vehicle_doc["plate_number"],
            brand=vehicle_doc["brand"],
            model=vehicle_doc["model"],
            year=vehicle_doc["year"],
            vehicle_class=vehicle_doc["vehicle_class"],
            price_per_day=vehicle_doc["price_per_day"],
            mileage=vehicle_doc["mileage"],
            branch_id=vehicle_doc["branch_id"],
            status=vehicle_doc["status"],
            created_at=vehicle_doc["created_at"],
            updated_at=vehicle_doc["updated_at"],
        )

    @staticmethod
    async def update_vehicle(
        vehicle_id: str, request: UpdateVehicleRequest
    ) -> Optional[VehicleData]:
        """
        Update vehicle information.

        Args:
            vehicle_id (str): Vehicle ID to update.
            request (UpdateVehicleRequest): Fields to update (only non-None fields).

        Returns:
            Optional[VehicleData]: Updated vehicle data or None if not found.

        Raises:
            DuplicateKeyError: If updating plate_number to existing value.
        """
        # Check if vehicle exists
        existing_vehicle = await db_manager.find_vehicle_by_id(vehicle_id)
        if not existing_vehicle:
            logger.info(f"Vehicle not found for update: {vehicle_id}")
            return None

        # Build update dict (only include non-None fields)
        update_data = {}
        if request.brand is not None:
            update_data["brand"] = request.brand
        if request.model is not None:
            update_data["model"] = request.model
        if request.vehicle_class is not None:
            update_data["vehicle_class"] = request.vehicle_class
        if request.price_per_day is not None:
            update_data["price_per_day"] = request.price_per_day
        if request.mileage is not None:
            update_data["mileage"] = request.mileage
        if request.branch_id is not None:
            update_data["branch_id"] = request.branch_id
        if request.status is not None:
            update_data["status"] = request.status.value

        # If no fields to update, return current data
        if not update_data:
            logger.info(f"No fields to update for vehicle: {vehicle_id}")
            return await VehicleService.get_vehicle_by_id(vehicle_id)

        # Update in database
        try:
            success = await db_manager.update_vehicle(vehicle_id, update_data)
            if not success:
                return None

            logger.info(f"Successfully updated vehicle: {vehicle_id}")
        except DuplicateKeyError:
            logger.error(f"Duplicate key error during update for vehicle: {vehicle_id}")
            raise

        # Return updated vehicle data
        return await VehicleService.get_vehicle_by_id(vehicle_id)

    @staticmethod
    async def delete_vehicle(vehicle_id: str) -> bool:
        """
        Delete a vehicle.

        Args:
            vehicle_id (str): Vehicle ID to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        success = await db_manager.delete_vehicle(vehicle_id)

        if success:
            logger.info(f"Successfully deleted vehicle: {vehicle_id}")
        else:
            logger.info(f"Vehicle not found for deletion: {vehicle_id}")

        return success

    @staticmethod
    async def list_vehicles(filters: VehicleFilterRequest) -> VehicleListData:
        """
        List vehicles with optional filters.

        Args:
            filters (VehicleFilterRequest): Filter criteria.

        Returns:
            VehicleListData: List of vehicles and total count.
        """
        # Build MongoDB query filters
        query_filters: Dict[str, Any] = {}

        if filters.vehicle_class is not None:
            query_filters["vehicle_class"] = filters.vehicle_class

        if filters.status is not None:
            query_filters["status"] = filters.status.value

        if filters.branch_id is not None:
            query_filters["branch_id"] = filters.branch_id

        # Price range filter
        if filters.min_price is not None or filters.max_price is not None:
            price_filter = {}
            if filters.min_price is not None:
                price_filter["$gte"] = filters.min_price
            if filters.max_price is not None:
                price_filter["$lte"] = filters.max_price
            query_filters["price_per_day"] = price_filter

        # Query database
        vehicle_docs = await db_manager.find_vehicles(query_filters)

        # Convert to response models
        vehicles = [
            VehicleData(
                id=doc["_id"],
                plate_number=doc["plate_number"],
                brand=doc["brand"],
                model=doc["model"],
                year=doc["year"],
                vehicle_class=doc["vehicle_class"],
                price_per_day=doc["price_per_day"],
                mileage=doc["mileage"],
                branch_id=doc["branch_id"],
                status=doc["status"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
            )
            for doc in vehicle_docs
        ]

        logger.info(f"Retrieved {len(vehicles)} vehicles with filters: {query_filters}")

        return VehicleListData(vehicles=vehicles, total_count=len(vehicles))


# Singleton instance
vehicle_service = VehicleService()
