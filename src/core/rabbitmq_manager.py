"""
RabbitMQ Manager

Minimal singleton manager for publishing and consuming domain events.
Handles connection lifecycle and provides simple publish/subscribe interface.

Author: Peyman Khodabandehlouei
Date: 13-01-2026
"""

import json
import logging
from typing import Optional, Callable, Dict, Any
from aio_pika.abc import AbstractIncomingMessage
from aio_pika import connect_robust, Message, Connection, Channel, Exchange

from core import config

logger = logging.getLogger(__name__)


class RabbitMQManager:
    """
    Singleton manager for RabbitMQ operations.

    Provides simple interface for publishing domain events and subscribing to them.
    Uses topic exchange for flexible event routing.
    """

    def __init__(self):
        """Initialize RabbitMQ manager (singleton pattern)."""
        self._connection: Optional[Connection] = None
        self._channel: Optional[Channel] = None
        self._exchange: Optional[Exchange] = None
        self._is_connected = False
        self._rabbitmq_url = config.rabbitmq.url.get_secret_value()
        self._exchange_name = config.rabbitmq.exchange_name

    async def connect(self) -> None:
        """
        Establish connection to RabbitMQ server.

        Creates connection, channel, and declares the exchange.
        Safe to call multiple times (idempotent).
        """
        if self._is_connected:
            logger.info("RabbitMQ already connected")
            return

        try:
            # Create robust connection
            self._connection = await connect_robust(self._rabbitmq_url)

            # Create a channel
            self._channel = await self._connection.channel()

            # Declare topic exchange
            self._exchange = await self._channel.declare_exchange(
                self._exchange_name, type="topic", durable=True
            )

            self._is_connected = True
            logger.info(f"Connected to RabbitMQ at {self._rabbitmq_url}")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self) -> None:
        """
        Close RabbitMQ connection gracefully.

        Safe to call even if not connected.
        """
        if not self._is_connected:
            return

        try:
            if self._connection and not self._connection.is_closed:
                await self._connection.close()

            self._connection = None
            self._channel = None
            self._exchange = None
            self._is_connected = False

            logger.info("Disconnected from RabbitMQ")

        except Exception as e:
            logger.error(f"Error during RabbitMQ disconnect: {e}")

    async def publish_event(
        self, event_type: str, data: Dict[str, Any], routing_key: Optional[str] = None
    ) -> None:
        """
        Publish a domain event to RabbitMQ.

        Events are published to the topic exchange with routing key matching event_type.
        Message body is JSON-serialized data with event metadata.

        Args:
            event_type (str): Event type (e.g., "reservation.confirmed")
            data (Dict[str, Any]): Event payload data
            routing_key (Optional[str]): Custom routing key (defaults to event_type)
        """
        if not self._is_connected:
            await self.connect()

        try:
            # Build message body with metadata
            message_body = {"event_type": event_type, "data": data, "timestamp": None}

            # Serialize to JSON
            message_bytes = json.dumps(message_body).encode()

            # Create a message with persistence
            message = Message(
                body=message_bytes, content_type="application/json", delivery_mode=2
            )

            # Publish to exchange
            routing_key = routing_key or event_type
            await self._exchange.publish(message, routing_key=routing_key)

            logger.info(
                f"Published event: {event_type} with routing key: {routing_key}"
            )

        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            raise

    async def subscribe(
        self,
        event_type: str,
        callback: Callable[[Dict[str, Any]], None],
        queue_name: Optional[str] = None,
    ) -> None:
        """
        Subscribe to domain events and process them with callback.

        Creates a durable queue, binds it to the exchange with event_type routing key,
        and processes incoming messages with the provided callback function.

        Args:
            event_type (str): Event type to subscribe to (supports wildcards: *, #)
            callback (Callable): Async function to handle event data
            queue_name (Optional[str]): Custom queue name (auto-generated if None)
        """
        if not self._is_connected:
            await self.connect()

        try:
            # Generate queue name if not provided
            if queue_name is None:
                queue_name = f"crfms_{event_type.replace('.', '_')}_queue"

            # Declare durable queue
            queue = await self._channel.declare_queue(
                queue_name, durable=True  # Survive broker restarts
            )

            # Bind queue to exchange with a routing key
            await queue.bind(exchange=self._exchange, routing_key=event_type)

            # Define message handler
            async def on_message(message: AbstractIncomingMessage):
                async with message.process():
                    try:
                        # Deserialize message body
                        body = json.loads(message.body.decode())
                        event_data = body.get("data", {})

                        logger.info(f"Received event: {event_type}")

                        # Call user-provided callback
                        await callback(event_data)

                    except Exception as e:
                        logger.error(f"Error processing event {event_type}: {e}")
                        # Message will be requeued if processing fails
                        raise

            # Start consuming messages
            await queue.consume(on_message)

            logger.info(f"Subscribed to event: {event_type} on queue: {queue_name}")

        except Exception as e:
            logger.error(f"Failed to subscribe to event {event_type}: {e}")
            raise


# Singleton instance
rabbitmq_manager = RabbitMQManager()
