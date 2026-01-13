"""
Database Manager Module

Provides a singleton MongoDB manager for async database operations with
connection pooling, retry logic, and health checks.

Usage:
    from shared.database_manager import db_manager

    # In async context:
    async with db_manager.get_session() as db:
        result = await db.books.find_one({"_id": task_id})

    # Or direct access:
    collection = db_manager.get_collection("books")
    await collection.insert_one(document)

Author: Peyman Khodabandehlouei
Last Update: 28-12-2025
"""

import asyncio
import logging
from datetime import date, time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List

from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    DuplicateKeyError,
)
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)

from core import config
from schemas.db_models import (
    CustomerDocument,
    EmployeeDocument,
    VehicleDocument,
    BranchDocument,
    AddOnDocument,
    InsuranceTierDocument,
    ReservationDocument,
    RentalDocument,
)


# Logger
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Singleton MongoDB manager with async support and connection pooling.

    This class manages the MongoDB connection lifecycle, provides connection
    pooling, automatic reconnection, and health checks.
    """

    _instance: Optional["DatabaseManager"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls) -> "DatabaseManager":
        """Ensure only one instance of DatabaseManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Construct a new DatabaseManager instance."""
        if not hasattr(self, "_initialized"):
            self._client: Optional[AsyncIOMotorClient] = None
            self._database: Optional[AsyncIOMotorDatabase] = None
            self._is_connected: bool = False
            self._initialized = True
            logger.info("DatabaseManager object initialized")

    async def connect(self) -> None:
        """
        Establish connection to MongoDB with retry logic.

        Creates a Motor async client with connection pooling.

        Raises:
            ConnectionFailure: If unable to connect after retries
        """
        # Validation
        if self._is_connected:
            logger.debug("Database already connected, skipping reconnection")
            return

        async with self._lock:
            # Double check connection after acquiring lock
            if self._is_connected:
                logger.debug("Database already connected, skipping reconnection")
                return

            try:
                db_uri = config.database.uri.get_secret_value()
                db_name = config.database.name

                logger.info("Connecting to the database.")

                self._client = AsyncIOMotorClient(
                    db_uri,
                    maxPoolSize=10,
                    minPoolSize=2,
                    maxIdleTimeMS=45000,
                    serverSelectionTimeoutMS=10000,
                    connectTimeoutMS=20000,
                    socketTimeoutMS=30000,
                    retryWrites=True,
                    retryReads=True,
                )

                # Get database instance
                self._database = self._client[db_name]

                # Test connection
                await self._client.admin.command("ping")

                self._is_connected = True
                logger.info("Successfully connected to the database.")

            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                self._is_connected = False
                raise

            except Exception as e:
                logger.error(f"Unexpected error during MongoDB connection: {e}")
                self._is_connected = False
                raise

    async def disconnect(self) -> None:
        """Close MongoDB connection and cleanup resources."""
        # Validation
        if not self._is_connected:
            logger.debug("Database already disconnected")
            return

        async with self._lock:
            if self._client:
                logger.info("Closing MongoDB connection")
                self._client.close()
                self._client = None
                self._database = None
                self._is_connected = False
                logger.info("MongoDB connection closed")

    async def health_check(self) -> bool:
        """
        Verify database connection is healthy.

        Returns:
            bool: True if the database is accessible, False otherwise
        """
        try:
            if not self._is_connected or not self._client:
                return False

            # Ping database with short timeout
            await asyncio.wait_for(self._client.admin.command("ping"), timeout=2.0)
            return True

        except asyncio.TimeoutError:
            logger.warning("Database health check timed out")
            return False
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    @asynccontextmanager
    async def get_session(self):
        """
        Context manager for database operations.

        Ensures connection is established before operations.

        Yields:
            AsyncIOMotorDatabase: Database instance

        Example:
            async with db_manager.get_session() as db:
                await db.books.insert_one({"title": "Example"})
        """
        if not self._is_connected:
            await self.connect()

        yield self._database

    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """
        Get a MongoDB collection instance.

        Args:
            collection_name (str): Name of the collection

        Returns:
            AsyncIOMotorCollection: Collection instance for async operations

        Raises:
            RuntimeError: If the database is not connected
        """
        if not self._is_connected or self._database is None:
            raise RuntimeError(
                "Database not connected. Call await db_manager.connect() first."
            )

        return self._database[collection_name]

    async def create_customer(self, customer_data: CustomerDocument) -> str:
        """
        Create a new customer in the database.

        Args:
            customer_data (CustomerDocument): Customer Pydantic model with validated data.

        Returns:
            str: The created customer ID

        Raises:
            DuplicateKeyError: If email already exists
            RuntimeError: If the database is not connected
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("customers")

            # Convert Pydantic model to dict for MongoDB
            customer_dict = customer_data.model_dump(by_alias=True, mode="json")

            result = await collection.insert_one(customer_dict)
            logger.info(f"Created customer with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except DuplicateKeyError:
            logger.warning(f"Duplicate email: {customer_data.email}")
            raise

        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            raise

    async def create_employee(self, employee_data: EmployeeDocument) -> str:
        """
        Create a new employee (agent or manager) in the database.

        Args:
            employee_data (EmployeeDocument): Employee Pydantic model with validated data.

        Returns:
            str: The created employee ID

        Raises:
            DuplicateKeyError: If email already exists
            RuntimeError: If the database is not connected
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("employees")

            # Convert Pydantic model to dict
            employee_dict = employee_data.model_dump(by_alias=True, mode="json")

            result = await collection.insert_one(employee_dict)
            logger.info(f"Created employee with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except DuplicateKeyError:
            logger.warning(f"Duplicate email: {employee_data.email}")
            raise

        except Exception as e:
            logger.error(f"Failed to create employee: {e}")
            raise

    async def find_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Find customer by ID"""
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("customers")
        return await collection.find_one({"_id": customer_id})

    async def find_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find customer by email"""
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("customers")
        return await collection.find_one({"email": email})

    async def find_employee_by_id(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Find employee by ID"""
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("employees")
        return await collection.find_one({"_id": employee_id})

    async def find_employee_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find employee by email - for login/duplicate check"""
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("employees")
        return await collection.find_one({"email": email})

    async def create_vehicle(self, vehicle_data: VehicleDocument) -> str:
        """
        Create a new vehicle in the database.

        Args:
            vehicle_data (VehicleDocument): Vehicle Pydantic model with validated data.

        Returns:
            str: The created vehicle ID

        Raises:
            DuplicateKeyError: If plate_number already exists
            RuntimeError: If the database is not connected
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("vehicles")

            # Convert Pydantic model to dict for MongoDB
            vehicle_dict = vehicle_data.model_dump(by_alias=True, mode="json")

            result = await collection.insert_one(vehicle_dict)
            logger.info(f"Created vehicle with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except DuplicateKeyError:
            logger.warning(f"Duplicate plate number: {vehicle_data.plate_number}")
            raise

        except Exception as e:
            logger.error(f"Failed to create vehicle: {e}")
            raise

    async def find_vehicle_by_id(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a vehicle by ID.

        Args:
            vehicle_id (str): Vehicle's unique identifier

        Returns:
            Optional[Dict[str, Any]]: Vehicle document or None if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("vehicles")
        return await collection.find_one({"_id": vehicle_id})

    async def find_vehicle_by_plate(
        self, plate_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a vehicle by plate number.

        Args:
            plate_number (str): Vehicle's plate number

        Returns:
            Optional[Dict[str, Any]]: Vehicle document or None if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("vehicles")
        return await collection.find_one({"plate_number": plate_number})

    async def update_vehicle(
        self, vehicle_id: str, update_data: Dict[str, Any]
    ) -> bool:
        """
        Update vehicle information.

        Args:
            vehicle_id (str): Vehicle ID to update
            update_data (Dict[str, Any]): Fields to update

        Returns:
            bool: True if vehicle was updated, False if not found

        Raises:
            DuplicateKeyError: If updating plate_number to existing value
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("vehicles")

            # Add updated_at timestamp
            update_data["updated_at"] = datetime.now(timezone.utc)

            result = await collection.update_one(
                {"_id": vehicle_id}, {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"Updated vehicle: {vehicle_id}")
                return True
            return False

        except DuplicateKeyError:
            logger.warning(
                f"Duplicate plate number in update: {update_data.get('plate_number')}"
            )
            raise

        except Exception as e:
            logger.error(f"Failed to update vehicle: {e}")
            raise

    async def delete_vehicle(self, vehicle_id: str) -> bool:
        """
        Delete a vehicle from the database.

        Args:
            vehicle_id (str): Vehicle ID to delete

        Returns:
            bool: True if vehicle was deleted, False if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("vehicles")
        result = await collection.delete_one({"_id": vehicle_id})

        if result.deleted_count > 0:
            logger.info(f"Deleted vehicle: {vehicle_id}")
            return True
        return False

    async def find_vehicles(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find vehicles with optional filters.

        Args:
            filters (Optional[Dict[str, Any]]): MongoDB query filters

        Returns:
            List[Dict[str, Any]]: List of vehicle documents
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("vehicles")

        if filters is None:
            filters = {}

        cursor = collection.find(filters).sort("created_at", -1)
        vehicles = await cursor.to_list(length=None)
        return vehicles

    async def create_branch(self, branch_data: BranchDocument) -> str:
        """
        Create a new branch in the database.

        Args:
            branch_data (BranchDocument): Branch Pydantic model with validated data.

        Returns:
            str: The created branch ID

        Raises:
            RuntimeError: If the database is not connected
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("branches")

            # Convert Pydantic model to dict for MongoDB
            branch_dict = branch_data.model_dump(by_alias=True, mode="json")

            result = await collection.insert_one(branch_dict)
            logger.info(f"Created branch with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Failed to create branch: {e}")
            raise

    async def find_branch_by_id(self, branch_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a branch by ID.

        Args:
            branch_id (str): Branch's unique identifier

        Returns:
            Optional[Dict[str, Any]]: Branch document or None if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("branches")
        return await collection.find_one({"_id": branch_id})

    async def find_branches(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find branches with optional filters.

        Args:
            filters (Optional[Dict[str, Any]]): MongoDB query filters

        Returns:
            List[Dict[str, Any]]: List of branch documents
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("branches")

        if filters is None:
            filters = {}

        cursor = collection.find(filters).sort("created_at", -1)
        branches = await cursor.to_list(length=None)
        return branches

    async def update_branch(self, branch_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update branch information.

        Args:
            branch_id (str): Branch ID to update
            update_data (Dict[str, Any]): Fields to update

        Returns:
            bool: True if branch was updated, False if not found
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("branches")

            # Add updated_at timestamp
            update_data["updated_at"] = datetime.now(timezone.utc)

            result = await collection.update_one(
                {"_id": branch_id}, {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"Updated branch: {branch_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to update branch: {e}")
            raise

    async def delete_branch(self, branch_id: str) -> bool:
        """
        Delete a branch from the database.

        Args:
            branch_id (str): Branch ID to delete

        Returns:
            bool: True if branch was deleted, False if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("branches")
        result = await collection.delete_one({"_id": branch_id})

        if result.deleted_count > 0:
            logger.info(f"Deleted branch: {branch_id}")
            return True
        return False

    async def add_employee_to_branch(self, branch_id: str, employee_id: str) -> bool:
        """
        Add an employee ID to a branch's employee_ids list.

        Args:
            branch_id (str): Branch ID
            employee_id (str): Employee ID to add

        Returns:
            bool: True if employee was added, False if branch not found
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("branches")

            result = await collection.update_one(
                {"_id": branch_id},
                {
                    "$addToSet": {"employee_ids": employee_id},  # Prevents duplicates
                    "$set": {"updated_at": datetime.now(timezone.utc)},
                },
            )

            if result.modified_count > 0:
                logger.info(f"Added employee {employee_id} to branch {branch_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to add employee to branch: {e}")
            raise

    async def remove_employee_from_branch(
        self, branch_id: str, employee_id: str
    ) -> bool:
        """
        Remove an employee ID from a branch's employee_ids list.

        Args:
            branch_id (str): Branch ID
            employee_id (str): Employee ID to remove

        Returns:
            bool: True if employee was removed, False if branch not found
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("branches")

            result = await collection.update_one(
                {"_id": branch_id},
                {
                    "$pull": {"employee_ids": employee_id},  # Remove from array
                    "$set": {"updated_at": datetime.now(timezone.utc)},
                },
            )

            if result.modified_count > 0:
                logger.info(f"Removed employee {employee_id} from branch {branch_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to remove employee from branch: {e}")
            raise

    async def create_add_on(self, add_on_data: AddOnDocument) -> str:
        """
        Create a new add-on in the database.

        Args:
            add_on_data (AddOnDocument): Add-on Pydantic model with validated data.

        Returns:
            str: The created add-on ID

        Raises:
            RuntimeError: If the database is not connected
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("add_ons")

            # Convert Pydantic model to dict for MongoDB
            add_on_dict = add_on_data.model_dump(by_alias=True, mode="json")

            result = await collection.insert_one(add_on_dict)
            logger.info(f"Created add-on with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Failed to create add-on: {e}")
            raise

    async def find_add_on_by_id(self, add_on_id: str) -> Optional[Dict[str, Any]]:
        """
        Find an add-on by ID.

        Args:
            add_on_id (str): Add-on's unique identifier

        Returns:
            Optional[Dict[str, Any]]: Add-on document or None if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("add_ons")
        return await collection.find_one({"_id": add_on_id})

    async def find_add_ons(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find add-ons with optional filters.

        Args:
            filters (Optional[Dict[str, Any]]): MongoDB query filters

        Returns:
            List[Dict[str, Any]]: List of add-on documents
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("add_ons")

        if filters is None:
            filters = {}

        cursor = collection.find(filters).sort("created_at", -1)
        add_ons = await cursor.to_list(length=None)
        return add_ons

    async def update_add_on(self, add_on_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update add-on information.

        Args:
            add_on_id (str): Add-on ID to update
            update_data (Dict[str, Any]): Fields to update

        Returns:
            bool: True if add-on was updated, False if not found
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("add_ons")

            # Add updated_at timestamp
            update_data["updated_at"] = datetime.now(timezone.utc)

            result = await collection.update_one(
                {"_id": add_on_id}, {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"Updated add-on: {add_on_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to update add-on: {e}")
            raise

    async def delete_add_on(self, add_on_id: str) -> bool:
        """
        Delete an add-on from the database.

        Args:
            add_on_id (str): Add-on ID to delete

        Returns:
            bool: True if add-on was deleted, False if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("add_ons")
        result = await collection.delete_one({"_id": add_on_id})

        if result.deleted_count > 0:
            logger.info(f"Deleted add-on: {add_on_id}")
            return True
        return False

    async def find_add_ons_by_ids(self, add_on_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Find multiple add-ons by their IDs.

        Args:
            add_on_ids (List[str]): List of add-on IDs to find

        Returns:
            List[Dict[str, Any]]: List of add-on documents
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("add_ons")
        cursor = collection.find({"_id": {"$in": add_on_ids}})
        add_ons = await cursor.to_list(length=None)
        return add_ons

    async def create_insurance_tier(self, tier_data: InsuranceTierDocument) -> str:
        """
        Create a new insurance tier in the database.

        Args:
            tier_data (InsuranceTierDocument): Insurance tier Pydantic model with validated data.

        Returns:
            str: The created insurance tier ID

        Raises:
            RuntimeError: If the database is not connected
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("insurance_tiers")

            # Convert Pydantic model to dict for MongoDB
            tier_dict = tier_data.model_dump(by_alias=True, mode="json")

            result = await collection.insert_one(tier_dict)
            logger.info(f"Created insurance tier with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Failed to create insurance tier: {e}")
            raise

    async def find_insurance_tier_by_id(self, tier_id: str) -> Optional[Dict[str, Any]]:
        """
        Find an insurance tier by ID.

        Args:
            tier_id (str): Insurance tier's unique identifier

        Returns:
            Optional[Dict[str, Any]]: Insurance tier document or None if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("insurance_tiers")
        return await collection.find_one({"_id": tier_id})

    async def find_insurance_tiers(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find insurance tiers with optional filters.

        Args:
            filters (Optional[Dict[str, Any]]): MongoDB query filters

        Returns:
            List[Dict[str, Any]]: List of insurance tier documents
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("insurance_tiers")

        if filters is None:
            filters = {}

        cursor = collection.find(filters).sort("created_at", -1)
        tiers = await cursor.to_list(length=None)
        return tiers

    async def update_insurance_tier(
        self, tier_id: str, update_data: Dict[str, Any]
    ) -> bool:
        """
        Update insurance tier information.

        Args:
            tier_id (str): Insurance tier ID to update
            update_data (Dict[str, Any]): Fields to update

        Returns:
            bool: True if tier was updated, False if not found
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("insurance_tiers")

            # Add updated_at timestamp
            update_data["updated_at"] = datetime.now(timezone.utc)

            result = await collection.update_one(
                {"_id": tier_id}, {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"Updated insurance tier: {tier_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to update insurance tier: {e}")
            raise

    async def delete_insurance_tier(self, tier_id: str) -> bool:
        """
        Delete an insurance tier from the database.

        Args:
            tier_id (str): Insurance tier ID to delete

        Returns:
            bool: True if tier was deleted, False if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("insurance_tiers")
        result = await collection.delete_one({"_id": tier_id})

        if result.deleted_count > 0:
            logger.info(f"Deleted insurance tier: {tier_id}")
            return True
        return False

    async def create_reservation(self, reservation_data: ReservationDocument) -> str:
        """
        Create a new reservation in the database.

        Args:
            reservation_data (ReservationDocument): Reservation Pydantic model with validated data.

        Returns:
            str: The created reservation ID

        Raises:
            RuntimeError: If the database is not connected
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("reservations")

            # Convert Pydantic model to dict for MongoDB
            reservation_dict = reservation_data.model_dump(by_alias=True, mode="json")

            result = await collection.insert_one(reservation_dict)
            logger.info(f"Created reservation with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Failed to create reservation: {e}")
            raise

    async def find_reservation_by_id(
        self, reservation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a reservation by ID.

        Args:
            reservation_id (str): Reservation's unique identifier

        Returns:
            Optional[Dict[str, Any]]: Reservation document or None if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("reservations")
        return await collection.find_one({"_id": reservation_id})

    async def find_reservations(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find reservations with optional filters.

        Args:
            filters (Optional[Dict[str, Any]]): MongoDB query filters

        Returns:
            List[Dict[str, Any]]: List of reservation documents
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("reservations")

        if filters is None:
            filters = {}

        cursor = collection.find(filters).sort("created_at", -1)
        reservations = await cursor.to_list(length=None)
        return reservations

    async def update_reservation(
        self, reservation_id: str, update_data: Dict[str, Any]
    ) -> bool:
        """
        Update reservation information.

        Args:
            reservation_id (str): Reservation ID to update
            update_data (Dict[str, Any]): Fields to update

        Returns:
            bool: True if reservation was updated, False if not found
        """
        if not self._is_connected:
            await self.connect()

        try:
            from datetime import time

            collection = self.get_collection("reservations")

            # FIX: Convert date objects to datetime for MongoDB storage
            if "pickup_date" in update_data and isinstance(
                update_data["pickup_date"], date
            ):
                update_data["pickup_date"] = datetime.combine(
                    update_data["pickup_date"], time.min
                )

            if "return_date" in update_data and isinstance(
                update_data["return_date"], date
            ):
                update_data["return_date"] = datetime.combine(
                    update_data["return_date"], time.max
                )

            # Add updated_at timestamp
            update_data["updated_at"] = datetime.now(timezone.utc)

            result = await collection.update_one(
                {"_id": reservation_id}, {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"Updated reservation: {reservation_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to update reservation: {e}")
            raise

    async def delete_reservation(self, reservation_id: str) -> bool:
        """
        Delete a reservation from the database.

        Args:
            reservation_id (str): Reservation ID to delete

        Returns:
            bool: True if reservation was deleted, False if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("reservations")
        result = await collection.delete_one({"_id": reservation_id})

        if result.deleted_count > 0:
            logger.info(f"Deleted reservation: {reservation_id}")
            return True
        return False

    async def find_reservations_by_customer(
        self, customer_id: str
    ) -> List[Dict[str, Any]]:
        """
        Find all reservations for a specific customer.

        Args:
            customer_id (str): Customer ID to filter by

        Returns:
            List[Dict[str, Any]]: List of reservation documents
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("reservations")
        cursor = collection.find({"customer_id": customer_id}).sort("created_at", -1)
        reservations = await cursor.to_list(length=None)
        return reservations

    async def find_reservations_by_vehicle(
        self, vehicle_id: str
    ) -> List[Dict[str, Any]]:
        """
        Find all reservations for a specific vehicle.

        Args:
            vehicle_id (str): Vehicle ID to filter by

        Returns:
            List[Dict[str, Any]]: List of reservation documents
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("reservations")
        cursor = collection.find({"vehicle_id": vehicle_id}).sort("pickup_date", 1)
        reservations = await cursor.to_list(length=None)
        return reservations

    async def check_vehicle_availability(
        self,
        vehicle_id: str,
        pickup_date: date,
        return_date: date,
        exclude_reservation_id: Optional[str] = None,
    ) -> bool:
        """
        Check if a vehicle is available for the given date range.

        A vehicle is unavailable if there's any reservation that overlaps
        with the requested dates.

        Date overlap logic:
        - Existing reservation overlaps if:
          (existing.pickup_date <= requested.return_date) AND
          (existing.return_date >= requested.pickup_date)

        Args:
            vehicle_id (str): Vehicle ID to check
            pickup_date (date): Requested pickup date
            return_date (date): Requested return date
            exclude_reservation_id (Optional[str]): Exclude this reservation ID
                (useful when updating existing reservation)

        Returns:
            bool: True if vehicle is available, False if already booked
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("reservations")

            # Convert date to datetime at start of day
            pickup_datetime = datetime.combine(pickup_date, time.min)
            return_datetime = datetime.combine(return_date, time.max)

            # Build query to find overlapping reservations
            query = {
                "vehicle_id": vehicle_id,
                "status": {"$in": ["pending", "confirmed"]},  # Only active reservations
                "pickup_date": {"$lte": return_datetime},
                "return_date": {"$gte": pickup_datetime},
            }

            # Exclude specific reservation (for updates)
            if exclude_reservation_id:
                query["_id"] = {"$ne": exclude_reservation_id}

            # Check if any overlapping reservations exist
            conflicting_reservation = await collection.find_one(query)

            is_available = conflicting_reservation is None

            if not is_available:
                logger.info(
                    f"Vehicle {vehicle_id} not available from {pickup_date} to {return_date}. "
                    f"Conflicts with reservation {conflicting_reservation['_id']}"
                )

            return is_available

        except Exception as e:
            logger.error(f"Failed to check vehicle availability: {e}")
            raise

    async def find_reservations_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Find all reservations with a specific status.

        Args:
            status (str): Status to filter by (pending/confirmed/cancelled/completed)

        Returns:
            List[Dict[str, Any]]: List of reservation documents
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("reservations")
        cursor = collection.find({"status": status}).sort("created_at", -1)
        reservations = await cursor.to_list(length=None)
        return reservations

    async def find_reservations_by_date_range(
        self,
        pickup_date_from: Optional[date] = None,
        pickup_date_to: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find reservations within a pickup date range.

        Args:
            pickup_date_from (Optional[date]): Start of date range (inclusive)
            pickup_date_to (Optional[date]): End of date range (inclusive)

        Returns:
            List[Dict[str, Any]]: List of reservation documents
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("reservations")
        query = {}

        if pickup_date_from or pickup_date_to:
            query["pickup_date"] = {}
            if pickup_date_from:
                query["pickup_date"]["$gte"] = datetime.combine(
                    pickup_date_from, time.min
                )
            if pickup_date_to:
                query["pickup_date"]["$lte"] = datetime.combine(
                    pickup_date_to, time.max
                )

        cursor = collection.find(query).sort("pickup_date", 1)
        reservations = await cursor.to_list(length=None)
        return reservations

    async def create_rental(self, rental_data: "RentalDocument") -> str:
        """
        Create a new rental in the database.

        Args:
            rental_data (RentalDocument): Rental Pydantic model with validated data.

        Returns:
            str: The created rental ID

        Raises:
            DuplicateKeyError: If pickup_token already exists (idempotency violation)
            RuntimeError: If the database is not connected
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("rentals")

            # Convert Pydantic model to dict for MongoDB
            rental_dict = rental_data.model_dump(by_alias=True, mode="json")

            result = await collection.insert_one(rental_dict)
            logger.info(f"Created rental with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except DuplicateKeyError:
            logger.warning(f"Duplicate pickup_token: {rental_data.pickup_token}")
            raise

        except Exception as e:
            logger.error(f"Failed to create rental: {e}")
            raise

    async def find_rental_by_id(self, rental_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a rental by ID.

        Args:
            rental_id (str): Rental's unique identifier

        Returns:
            Optional[Dict[str, Any]]: Rental document or None if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("rentals")
        return await collection.find_one({"_id": rental_id})

    async def find_rental_by_pickup_token(
        self, pickup_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a rental by pickup token.

        Used for idempotent pickup operations - if a rental with this token
        already exists, return it instead of creating a duplicate.

        Args:
            pickup_token (str): Unique pickup token

        Returns:
            Optional[Dict[str, Any]]: Rental document or None if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("rentals")
        return await collection.find_one({"pickup_token": pickup_token})

    async def find_rentals(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find rentals with optional filters.

        Common filters:
            - customer_id: Filter by customer
            - vehicle_id: Filter by vehicle
            - agent_id: Filter by agent who processed pickup
            - status: Filter by rental status (active/completed)
            - reservation_id: Filter by associated reservation

        Args:
            filters (Optional[Dict[str, Any]]): MongoDB query filters

        Returns:
            List[Dict[str, Any]]: List of rental documents sorted by created_at (newest first)
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("rentals")

        if filters is None:
            filters = {}

        cursor = collection.find(filters).sort("created_at", -1)
        rentals = await cursor.to_list(length=None)
        return rentals

    async def update_rental(self, rental_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update rental information.

        Typically used to:
        - Add return_readings when vehicle is returned
        - Add charges after return calculation
        - Update status from 'active' to 'completed'

        Args:
            rental_id (str): Rental ID to update
            update_data (Dict[str, Any]): Fields to update

        Returns:
            bool: True if rental was updated, False if not found
        """
        if not self._is_connected:
            await self.connect()

        try:
            collection = self.get_collection("rentals")

            # Add updated_at timestamp
            update_data["updated_at"] = datetime.now(timezone.utc)

            result = await collection.update_one(
                {"_id": rental_id}, {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"Updated rental: {rental_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to update rental: {e}")
            raise

    async def find_rental_by_reservation(
        self, reservation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find rental by associated reservation ID.

        Useful for checking if a reservation has already been picked up.

        Args:
            reservation_id (str): Reservation ID

        Returns:
            Optional[Dict[str, Any]]: Rental document or None if not found
        """
        if not self._is_connected:
            await self.connect()

        collection = self.get_collection("rentals")
        return await collection.find_one({"reservation_id": reservation_id})

    async def check_rental_extension_conflict(
        self,
        vehicle_id: str,
        current_return_date: date,
        new_return_date: date,
        exclude_reservation_id: str,
    ) -> bool:
        """
        Check if extending a rental would conflict with another reservation.

        Used when customer wants to extend their rental - ensures the vehicle
        doesn't have another reservation scheduled during the extension period.

        Business Logic:
            - Check reservations for same vehicle
            - Between current_return_date and new_return_date
            - Exclude the current reservation
            - Only check 'pending', 'confirmed', or 'approved' reservations

        Args:
            vehicle_id (str): Vehicle ID to check
            current_return_date (date): Current planned return date
            new_return_date (date): Requested new return date
            exclude_reservation_id (str): Current reservation ID (don't check against itself)

        Returns:
            bool: True if extension is possible (no conflicts), False if conflicts exist
        """
        if not self._is_connected:
            await self.connect()

        try:
            from datetime import time

            collection = self.get_collection("reservations")

            # Convert dates to datetime for MongoDB comparison
            current_datetime = datetime.combine(current_return_date, time.min)
            new_datetime = datetime.combine(new_return_date, time.max)

            # Find conflicting reservations
            # A reservation conflicts if it starts before new_return_date
            # and ends after current_return_date
            query = {
                "vehicle_id": vehicle_id,
                "status": {"$in": ["pending", "confirmed", "approved"]},
                "pickup_date": {"$lte": new_datetime},
                "return_date": {"$gte": current_datetime},
                "_id": {"$ne": exclude_reservation_id},
            }

            conflicting_reservation = await collection.find_one(query)

            if conflicting_reservation:
                logger.info(
                    f"Extension conflict: Vehicle {vehicle_id} has reservation "
                    f"{conflicting_reservation['_id']} from "
                    f"{conflicting_reservation['pickup_date']} to "
                    f"{conflicting_reservation['return_date']}"
                )
                return False  # Conflict exists

            return True  # No conflicts, extension is possible

        except Exception as e:
            logger.error(f"Failed to check rental extension conflict: {e}")
            raise

    async def find_all_customers(self) -> List[Dict[str, Any]]:
        """
        Retrieve all customers from the database.

        Returns:
            List[Dict[str, Any]]: List of customer documents.
        """
        collection = self.get_collection("customers")

        return await collection.find({"role": "customer"}).to_list(None)

    async def find_all_employees(self) -> List[Dict[str, Any]]:
        """
        Retrieve all employees (agents and managers) from the database.

        Returns:
            List[Dict[str, Any]]: List of employee documents.
        """
        collection = self.get_collection("employees")

        return await collection.find({"role": {"$in": ["agent", "manager"]}}).to_list(
            None
        )


# Create singleton instance
db_manager = DatabaseManager()
