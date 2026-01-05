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
from schemas.db_models import CustomerDocument, EmployeeDocument, VehicleDocument


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


# Create singleton instance
db_manager = DatabaseManager()
