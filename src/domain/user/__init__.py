"""
This module provides public API for User domain including BaseUser,
Employee, Agent, Manager, and Customer.

Author: Peyman Khodabandehlouei
"""

# Import modules
from domain.user.base_user import BaseUser
from domain.user.employee import Employee
from domain.user.agent import Agent
from domain.user.manager import Manager
from domain.user.customer import Customer


# Public API
__all__ = [
    "BaseUser",
    "Employee",
    "Agent",
    "Manager",
    "Customer",
]
