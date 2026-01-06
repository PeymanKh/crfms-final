"""
Add-on Service

Handles add-on management operations including CRUD logic.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from core.database_manager import db_manager
from schemas.db_models.add_on_models import AddOnDocument
from schemas.api.requests import (
    CreateAddOnRequest,
    UpdateAddOnRequest,
)
from schemas.api.responses import AddOnData, AddOnListData

logger = logging.getLogger(__name__)


class AddOnService:
    """
    Service for add-on management operations.

    Handles business logic for creating, reading, updating, and deleting add-ons.
    """

    @staticmethod
    async def create_add_on(request: CreateAddOnRequest) -> AddOnData:
        """
        Create a new add-on.

        Args:
            request (CreateAddOnRequest): Validated add-on creation data.

        Returns:
            AddOnData: Created add-on data for response.
        """
        # Generate add-on ID
        add_on_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)

        # Create database document
        add_on_doc = AddOnDocument(
            _id=add_on_id,
            name=request.name,
            description=request.description,
            price_per_day=request.price_per_day,
            created_at=current_time,
            updated_at=current_time,
        )

        # Save to database
        try:
            await db_manager.create_add_on(add_on_doc)
            logger.info(f"Successfully created add-on: {add_on_id}")
        except Exception as e:
            logger.error(f"Failed to create add-on: {e}")
            raise

        # Return response data
        return AddOnData(
            id=add_on_id,
            name=request.name,
            description=request.description,
            price_per_day=request.price_per_day,
            created_at=current_time,
            updated_at=current_time,
        )

    @staticmethod
    async def get_add_on_by_id(add_on_id: str) -> Optional[AddOnData]:
        """
        Get add-on by ID.

        Args:
            add_on_id (str): Add-on's unique identifier.

        Returns:
            Optional[AddOnData]: Add-on data or None if not found.
        """
        add_on_doc = await db_manager.find_add_on_by_id(add_on_id)

        if not add_on_doc:
            logger.info(f"Add-on not found: {add_on_id}")
            return None

        # Convert MongoDB document to response model
        return AddOnData(
            id=add_on_doc["_id"],
            name=add_on_doc["name"],
            description=add_on_doc["description"],
            price_per_day=add_on_doc["price_per_day"],
            created_at=add_on_doc["created_at"],
            updated_at=add_on_doc["updated_at"],
        )

    @staticmethod
    async def update_add_on(
        add_on_id: str, request: UpdateAddOnRequest
    ) -> Optional[AddOnData]:
        """
        Update add-on information.

        Args:
            add_on_id (str): Add-on ID to update.
            request (UpdateAddOnRequest): Fields to update (only non-None fields).

        Returns:
            Optional[AddOnData]: Updated add-on data or None if not found.
        """
        # Check if add-on exists
        existing_add_on = await db_manager.find_add_on_by_id(add_on_id)
        if not existing_add_on:
            logger.info(f"Add-on not found for update: {add_on_id}")
            return None

        # Build update dict (only include non-None fields)
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.description is not None:
            update_data["description"] = request.description
        if request.price_per_day is not None:
            update_data["price_per_day"] = request.price_per_day

        # If no fields to update, return current data
        if not update_data:
            logger.info(f"No fields to update for add-on: {add_on_id}")
            return await AddOnService.get_add_on_by_id(add_on_id)

        # Update in database
        try:
            success = await db_manager.update_add_on(add_on_id, update_data)
            if not success:
                return None

            logger.info(f"Successfully updated add-on: {add_on_id}")
        except Exception as e:
            logger.error(f"Failed to update add-on: {e}")
            raise

        # Return updated add-on data
        return await AddOnService.get_add_on_by_id(add_on_id)

    @staticmethod
    async def delete_add_on(add_on_id: str) -> bool:
        """
        Delete an add-on.

        Args:
            add_on_id (str): Add-on ID to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        success = await db_manager.delete_add_on(add_on_id)

        if success:
            logger.info(f"Successfully deleted add-on: {add_on_id}")
        else:
            logger.info(f"Add-on not found for deletion: {add_on_id}")

        return success

    @staticmethod
    async def list_add_ons() -> AddOnListData:
        """
        List all add-ons.

        Returns:
            AddOnListData: List of add-ons and total count.
        """
        # Query database
        add_on_docs = await db_manager.find_add_ons()

        # Convert to response models
        add_ons = [
            AddOnData(
                id=doc["_id"],
                name=doc["name"],
                description=doc["description"],
                price_per_day=doc["price_per_day"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
            )
            for doc in add_on_docs
        ]

        logger.info(f"Retrieved {len(add_ons)} add-ons")

        return AddOnListData(add_ons=add_ons, total_count=len(add_ons))


# Singleton instance
add_on_service = AddOnService()
