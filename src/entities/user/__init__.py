"""
This module provides public API for User entities including BaseUser,
Employee, Agent, Manager, and Customer.

Author: Peyman Khodabandehlouei
"""

# Import modules
from entities.user.base_user import BaseUser
from entities.user.employee import Employee
from entities.user.agent import Agent
from entities.user.manager import Manager
from entities.user.customer import Customer


# Public API
__all__ = [
    "BaseUser",
    "Employee",
    "Agent",
    "Manager",
    "Customer",
]
