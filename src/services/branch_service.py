"""
Branch Service

Handles branch management operations including CRUD logic.

Author: Peyman Khodabandehlouei
Date: 05-01-2026
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from core.database_manager import db_manager
from schemas.db_models.branch_models import BranchDocument
from schemas.api.responses.branches import BranchData, BranchListData
from schemas.api.requests import CreateBranchRequest, UpdateBranchRequest


# Logger
logger = logging.getLogger(__name__)


class BranchService:
    """
    Service for branch management operations.

    Handles business logic for creating, reading, updating, and deleting branches.
    """

    @staticmethod
    async def create_branch(request: CreateBranchRequest) -> BranchData:
        """
        Create a new branch.

        Args:
            request (CreateBranchRequest): Validated branch creation data.

        Returns:
            BranchData: Created branch data for response.
        """
        # Generate branch ID
        branch_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)

        # Create database document
        branch_doc = BranchDocument(
            _id=branch_id,
            name=request.name,
            city=request.city,
            address=request.address,
            phone_number=request.phone_number,
            employee_ids=[],  # Empty on creation
            created_at=current_time,
            updated_at=current_time,
        )

        # Save to database
        try:
            await db_manager.create_branch(branch_doc)
            logger.info(f"Successfully created branch: {branch_id}")
        except Exception as e:
            logger.error(f"Failed to create branch: {e}")
            raise

        # Return response data
        return BranchData(
            id=branch_id,
            name=request.name,
            city=request.city,
            address=request.address,
            phone_number=request.phone_number,
            employee_count=0,  # No employees on creation
            created_at=current_time,
            updated_at=current_time,
        )

    @staticmethod
    async def get_branch_by_id(branch_id: str) -> Optional[BranchData]:
        """
        Get branch by ID.

        Args:
            branch_id (str): Branch's unique identifier.

        Returns:
            Optional[BranchData]: Branch data or None if not found.
        """
        branch_doc = await db_manager.find_branch_by_id(branch_id)

        if not branch_doc:
            logger.info(f"Branch not found: {branch_id}")
            return None

        # Convert MongoDB document to response model
        return BranchData(
            id=branch_doc["_id"],
            name=branch_doc["name"],
            city=branch_doc["city"],
            address=branch_doc["address"],
            phone_number=branch_doc["phone_number"],
            employee_count=len(branch_doc.get("employee_ids", [])),
            created_at=branch_doc["created_at"],
            updated_at=branch_doc["updated_at"],
        )

    @staticmethod
    async def update_branch(
        branch_id: str, request: UpdateBranchRequest
    ) -> Optional[BranchData]:
        """
        Update branch information.

        Args:
            branch_id (str): Branch ID to update.
            request (UpdateBranchRequest): Fields to update (only non-None fields).

        Returns:
            Optional[BranchData]: Updated branch data or None if not found.
        """
        # Check if branch exists
        existing_branch = await db_manager.find_branch_by_id(branch_id)
        if not existing_branch:
            logger.info(f"Branch not found for update: {branch_id}")
            return None

        # Build update dict (only include non-None fields)
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.city is not None:
            update_data["city"] = request.city
        if request.address is not None:
            update_data["address"] = request.address
        if request.phone_number is not None:
            update_data["phone_number"] = request.phone_number

        # If no fields to update, return current data
        if not update_data:
            logger.info(f"No fields to update for branch: {branch_id}")
            return await BranchService.get_branch_by_id(branch_id)

        # Update in database
        try:
            success = await db_manager.update_branch(branch_id, update_data)
            if not success:
                return None

            logger.info(f"Successfully updated branch: {branch_id}")
        except Exception as e:
            logger.error(f"Failed to update branch: {e}")
            raise

        # Return updated branch data
        return await BranchService.get_branch_by_id(branch_id)

    @staticmethod
    async def delete_branch(branch_id: str) -> bool:
        """
        Delete a branch.

        Args:
            branch_id (str): Branch ID to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        success = await db_manager.delete_branch(branch_id)

        if success:
            logger.info(f"Successfully deleted branch: {branch_id}")
        else:
            logger.info(f"Branch not found for deletion: {branch_id}")

        return success

    @staticmethod
    async def list_branches() -> BranchListData:
        """
        List all branches.

        Returns:
            BranchListData: List of branches and total count.
        """
        # Query database (no filters for now)
        branch_docs = await db_manager.find_branches()

        # Convert to response models
        branches = [
            BranchData(
                id=doc["_id"],
                name=doc["name"],
                city=doc["city"],
                address=doc["address"],
                phone_number=doc["phone_number"],
                employee_count=len(doc.get("employee_ids", [])),
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
            )
            for doc in branch_docs
        ]

        logger.info(f"Retrieved {len(branches)} branches")

        return BranchListData(branches=branches, total_count=len(branches))


# Singleton instance
branch_service = BranchService()
