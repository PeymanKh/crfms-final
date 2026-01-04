"""
This module implements Subscriber Interface,
which is an interface for application's notificationManager subscribers and can receive
notification based on specific events.

Author: Peyman Khodabandehlouei
Date: 09-11-2025
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from entities.notification import NotificationManagerInterface


class Subscriber(ABC):
    """Abstract Subscriber Interface"""

    @abstractmethod
    def update(self, subject: "NotificationManagerInterface"):
        """Update state and notify"""
        pass
