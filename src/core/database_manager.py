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
from typing import Optional
from contextlib import asynccontextmanager

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)

from core import config


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


# Create singleton instance
db_manager = DatabaseManager()
