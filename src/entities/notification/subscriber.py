"""
This module implements concrete agent and user subscribers, They will receive notifications
based on specific events in the application.

Author: Peyman Khodabandehlouei
Date: 09-11-2025
"""

from typing import TYPE_CHECKING

from entities.notification import Subscriber

if TYPE_CHECKING:
    from entities.notification import NotificationManagerInterface


class CustomerSubscriber(Subscriber):
    """Concrete Subscriber. It notifies students about new assignments"""

    def update(self, subject: "NotificationManagerInterface") -> str:
        return "Notification sent to the customer"


class AgentSubscriber(Subscriber):
    """Concrete Subscriber. It notifies students about new assignments"""

    def update(self, subject: "NotificationManagerInterface") -> str:
        return "Notification sent to the agent"
