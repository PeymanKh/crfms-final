"""
This module implements NotificationManagerInterface class,
which is an interface for application's notification managers.

Author: Peyman Khodabandehlouei
Date: 09-11-2025
"""

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from domain.notification import Subscriber


class NotificationManagerInterface(ABC):
    """Subject Interface. It manages subscribers"""

    @abstractmethod
    def attach(self, subscriber: "Subscriber"):
        """Attach a new subscriber"""
        pass

    @abstractmethod
    def detach(self, subscriber: "Subscriber"):
        """Detach an existing subscriber"""
        pass

    @abstractmethod
    def notify(self):
        """Notify all subscribers about an event"""
        pass
