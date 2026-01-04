"""
This module provides public API for Notification entities including
NotificationManagerInterface, Subscriber, CustomerSubscriber,
AgentSubscriber, and ConcreteNotificationManager

Author: Peyman Khodabandehlouei
"""

# Import modules
from entities.notification.notification_manager_interface import (
    NotificationManagerInterface,
)
from entities.notification.subscriber_interface import Subscriber
from entities.notification.subscriber import CustomerSubscriber, AgentSubscriber
from entities.notification.notification_manager import ConcreteNotificationManager


# Public API
__all__ = [
    "Subscriber",
    "AgentSubscriber",
    "CustomerSubscriber",
    "ConcreteNotificationManager",
    "NotificationManagerInterface",
]
