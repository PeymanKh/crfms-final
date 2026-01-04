"""
This module provides a clock service abstraction to handle time related operations.
It includes a system clock for production use and a fake clock for testing.

Author: Peyman Khodabandehlouei
"""

from abc import ABC, abstractmethod
from datetime import datetime, date


class ClockService(ABC):
    @abstractmethod
    def now(self) -> datetime:
        """Returns current datetime"""
        pass

    @abstractmethod
    def today(self) -> date:
        """Returns current date"""
        pass


class SystemClock(ClockService):
    """Production clock using system time"""

    def now(self) -> datetime:
        return datetime.now()

    def today(self) -> date:
        return date.today()


class FakeClock(ClockService):
    """Test clock with fixed time"""

    def __init__(self, fixed_time: datetime):
        self._fixed_time = fixed_time

    def now(self) -> datetime:
        return self._fixed_time

    def today(self) -> date:
        return self._fixed_time.date()

    def advance(self, **kwargs):
        """Advance time by timedelta kwargs"""
        from datetime import timedelta

        self._fixed_time += timedelta(**kwargs)
