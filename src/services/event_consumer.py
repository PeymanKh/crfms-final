"""
Event Consumer Service

Listens to domain events and triggers side effects (notifications, logging, etc).

Author: Peyman Khodabandehlouei
Date: 13-01-2026
"""

import logging
from typing import Dict, Any
from core import rabbitmq_manager
from schemas.domain import EventTypes

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Consumer for domain events.

    Handles notifications and other side effects triggered by domain events.
    """

    @staticmethod
    async def handle_reservation_confirmed(data: Dict[str, Any]):
        """Handle ReservationConfirmed event."""
        logger.info(
            f"📧 [EVENT] Reservation {data['reservation_id']} confirmed "
            f"for customer {data['customer_id']} | Total: ${data['total_price']}"
        )
        # TODO: Send email/SMS notification to customer

    @staticmethod
    async def handle_reservation_modified(data: Dict[str, Any]):
        """Handle ReservationModified event."""
        logger.info(f"✏️ [EVENT] Reservation {data['reservation_id']} was modified")
        # TODO: Send modification notification

    @staticmethod
    async def handle_pickup_completed(data: Dict[str, Any]):
        """Handle PickupCompleted event."""
        logger.info(
            f"🚗 [EVENT] Vehicle picked up | Rental: {data['rental_id']} | "
            f"Odometer: {data['odometer_reading']}km | Fuel: {data['fuel_level']}"
        )
        # TODO: Send pickup confirmation to customer

    @staticmethod
    async def handle_return_completed(data: Dict[str, Any]):
        """Handle ReturnCompleted event."""
        logger.info(
            f"🏁 [EVENT] Vehicle returned | Rental: {data['rental_id']} | "
            f"Total charges: ${data['total_charges']:.2f}"
        )
        # TODO: Send receipt to customer

    @staticmethod
    async def handle_invoice_paid(data: Dict[str, Any]):
        """Handle InvoicePaid event."""
        logger.info(
            f"✅ [EVENT] Invoice {data['invoice_id']} paid successfully | "
            f"Amount: ${data['amount']:.2f} | Method: {data['payment_method']}"
        )
        # TODO: Send payment confirmation

    @staticmethod
    async def handle_invoice_payment_failed(data: Dict[str, Any]):
        """Handle InvoicePaymentFailed event."""
        logger.error(
            f"❌ [EVENT] Payment FAILED for invoice {data['invoice_id']} | "
            f"Amount: ${data['amount']:.2f}"
        )
        # TODO: Send payment failure notification

    @staticmethod
    async def start_consuming():
        """
        Start consuming all domain events.

        Subscribe to all relevant events and register handlers.
        """
        logger.info("Starting event consumer...")

        # Subscribe to reservation events
        await rabbitmq_manager.subscribe(
            event_type=EventTypes.RESERVATION_CONFIRMED,
            callback=EventConsumer.handle_reservation_confirmed,
        )

        await rabbitmq_manager.subscribe(
            event_type=EventTypes.RESERVATION_MODIFIED,
            callback=EventConsumer.handle_reservation_modified,
        )

        # Subscribe to rental events
        await rabbitmq_manager.subscribe(
            event_type=EventTypes.PICKUP_COMPLETED,
            callback=EventConsumer.handle_pickup_completed,
        )

        await rabbitmq_manager.subscribe(
            event_type=EventTypes.RETURN_COMPLETED,
            callback=EventConsumer.handle_return_completed,
        )

        # Subscribe to payment events
        await rabbitmq_manager.subscribe(
            event_type=EventTypes.INVOICE_PAID,
            callback=EventConsumer.handle_invoice_paid,
        )

        await rabbitmq_manager.subscribe(
            event_type=EventTypes.INVOICE_PAYMENT_FAILED,
            callback=EventConsumer.handle_invoice_payment_failed,
        )

        logger.info("✅ Event consumer started successfully")


# Singleton instance
event_consumer = EventConsumer()
