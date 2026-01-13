"""
Domain Event Definitions

Defines all domain events published by the CRFMS system.

Author: Peyman Khodabandehlouei
Date: 13-01-2026
"""

from typing import Dict, Any


class DomainEvent:
    """Base class for domain events (optional, for type hints)."""

    event_type: str
    data: Dict[str, Any]


class EventTypes:
    """Domain event type constants."""

    # Reservation events
    RESERVATION_CONFIRMED = "reservation.confirmed"
    RESERVATION_MODIFIED = "reservation.modified"
    RESERVATION_CANCELLED = "reservation.cancelled"
    RESERVATION_APPROVED = "reservation.approved"

    # Rental events
    PICKUP_COMPLETED = "rental.pickup_completed"
    RETURN_COMPLETED = "rental.return_completed"
    RENTAL_EXTENDED = "rental.extended"
    OVERDUE_RETURN_DETECTED = "rental.overdue_detected"

    # Payment events
    INVOICE_PAID = "invoice.paid"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"
    DEPOSIT_AUTHORIZED = "deposit.authorized"
    DEPOSIT_CAPTURED = "deposit.captured"

    # Notification events
    NOTIFICATION_REQUIRED = "notification.required"
