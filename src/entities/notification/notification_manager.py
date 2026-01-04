"""
This module contains the concrete implementation of the NotificationManager,
which can directly initialize and used in the app.

Author: Peyman Khodabandehlouei
Date: 09-11-2025
"""

from typing import List, TYPE_CHECKING
from entities.notification import NotificationManagerInterface


if TYPE_CHECKING:
    from entities.notification import Subscriber


class ConcreteNotificationManager(NotificationManagerInterface):
    """Concrete Subject. It manages subscribers"""

    def __init__(self):
        self._subscribers: List["Subscriber"] = []

    @property
    def subscribers(self) -> List["Subscriber"]:
        return self._subscribers.copy()

    def attach(self, subscriber: "Subscriber"):
        self._subscribers.append(subscriber)

    def detach(self, subscriber: "Subscriber"):
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)

    def notify(self):
        for subscriber in self._subscribers:
            subscriber.update(self)
