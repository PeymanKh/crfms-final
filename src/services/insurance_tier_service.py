"""
Insurance Tier Service

Handles insurance tier management operations including CRUD logic.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from core.database_manager import db_manager
from schemas.db_models import InsuranceTierDocument
from schemas.api.responses import InsuranceTierData, InsuranceTierListData
from schemas.api.requests import (
    CreateInsuranceTierRequest,
    UpdateInsuranceTierRequest,
)

logger = logging.getLogger(__name__)


class InsuranceTierService:
    """
    Service for insurance tier management operations.

    Handles business logic for creating, reading, updating, and deleting insurance tiers.
    """

    @staticmethod
    async def create_insurance_tier(
        request: CreateInsuranceTierRequest,
    ) -> InsuranceTierData:
        """
        Create a new insurance tier.

        Args:
            request (CreateInsuranceTierRequest): Validated tier creation data.

        Returns:
            InsuranceTierData: Created tier data for response.
        """
        # Generate tier ID
        tier_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)

        # Create database document
        tier_doc = InsuranceTierDocument(
            _id=tier_id,
            tier_name=request.tier_name,
            description=request.description,
            price_per_day=request.price_per_day,
            created_at=current_time,
            updated_at=current_time,
        )

        # Save to database
        try:
            await db_manager.create_insurance_tier(tier_doc)
            logger.info(f"Successfully created insurance tier: {tier_id}")
        except Exception as e:
            logger.error(f"Failed to create insurance tier: {e}")
            raise

        # Return response data
        return InsuranceTierData(
            id=tier_id,
            tier_name=request.tier_name,
            description=request.description,
            price_per_day=request.price_per_day,
            created_at=current_time,
            updated_at=current_time,
        )

    @staticmethod
    async def get_insurance_tier_by_id(tier_id: str) -> Optional[InsuranceTierData]:
        """
        Get insurance tier by ID.

        Args:
            tier_id (str): Insurance tier's unique identifier.

        Returns:
            Optional[InsuranceTierData]: Tier data or None if not found.
        """
        tier_doc = await db_manager.find_insurance_tier_by_id(tier_id)

        if not tier_doc:
            logger.info(f"Insurance tier not found: {tier_id}")
            return None

        # Convert MongoDB document to response model
        return InsuranceTierData(
            id=tier_doc["_id"],
            tier_name=tier_doc["tier_name"],
            description=tier_doc["description"],
            price_per_day=tier_doc["price_per_day"],
            created_at=tier_doc["created_at"],
            updated_at=tier_doc["updated_at"],
        )

    @staticmethod
    async def update_insurance_tier(
        tier_id: str, request: UpdateInsuranceTierRequest
    ) -> Optional[InsuranceTierData]:
        """
        Update insurance tier information.

        Args:
            tier_id (str): Tier ID to update.
            request (UpdateInsuranceTierRequest): Fields to update (only non-None fields).

        Returns:
            Optional[InsuranceTierData]: Updated tier data or None if not found.
        """
        # Check if tier exists
        existing_tier = await db_manager.find_insurance_tier_by_id(tier_id)
        if not existing_tier:
            logger.info(f"Insurance tier not found for update: {tier_id}")
            return None

        # Build update dict (only include non-None fields)
        update_data = {}
        if request.tier_name is not None:
            update_data["tier_name"] = request.tier_name
        if request.description is not None:
            update_data["description"] = request.description
        if request.price_per_day is not None:
            update_data["price_per_day"] = request.price_per_day

        # If no fields to update, return current data
        if not update_data:
            logger.info(f"No fields to update for insurance tier: {tier_id}")
            return await InsuranceTierService.get_insurance_tier_by_id(tier_id)

        # Update in database
        try:
            success = await db_manager.update_insurance_tier(tier_id, update_data)
            if not success:
                return None

            logger.info(f"Successfully updated insurance tier: {tier_id}")
        except Exception as e:
            logger.error(f"Failed to update insurance tier: {e}")
            raise

        # Return updated tier data
        return await InsuranceTierService.get_insurance_tier_by_id(tier_id)

    @staticmethod
    async def delete_insurance_tier(tier_id: str) -> bool:
        """
        Delete an insurance tier.

        Args:
            tier_id (str): Tier ID to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        success = await db_manager.delete_insurance_tier(tier_id)

        if success:
            logger.info(f"Successfully deleted insurance tier: {tier_id}")
        else:
            logger.info(f"Insurance tier not found for deletion: {tier_id}")

        return success

    @staticmethod
    async def list_insurance_tiers() -> InsuranceTierListData:
        """
        List all insurance tiers.

        Returns:
            InsuranceTierListData: List of tiers and total count.
        """
        # Query database
        tier_docs = await db_manager.find_insurance_tiers()

        # Convert to response models
        tiers = [
            InsuranceTierData(
                id=doc["_id"],
                tier_name=doc["tier_name"],
                description=doc["description"],
                price_per_day=doc["price_per_day"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
            )
            for doc in tier_docs
        ]

        logger.info(f"Retrieved {len(tiers)} insurance tiers")

        return InsuranceTierListData(insurance_tiers=tiers, total_count=len(tiers))


# Singleton instance
insurance_tier_service = InsuranceTierService()
