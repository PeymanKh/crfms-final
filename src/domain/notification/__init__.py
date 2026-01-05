"""
This module provides public API for Notification domain including
NotificationManagerInterface, Subscriber, CustomerSubscriber,
AgentSubscriber, and ConcreteNotificationManager

Author: Peyman Khodabandehlouei
"""

# Import modules
from domain.notification.notification_manager_interface import (
    NotificationManagerInterface,
)
from domain.notification.subscriber_interface import Subscriber
from domain.notification.subscriber import CustomerSubscriber, AgentSubscriber
from domain.notification.notification_manager import ConcreteNotificationManager


# Public API
__all__ = [
    "Subscriber",
    "AgentSubscriber",
    "CustomerSubscriber",
    "ConcreteNotificationManager",
    "NotificationManagerInterface",
]
