"""
Configuration Management Module

This module handles secure loading and validation of environment variables.

Usage:
    from config.config import config

    if config.is_production():
        # Production-specific business logic
        pass

Author: Peyman Khodabandehlouei
Last Update: 20-12-2025
"""

import sys
import logging
from enum import Enum
from pathlib import Path

from pydantic import SecretStr, Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Standard logging levels for application logging configuration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseModel):
    """
    Database connection configuration.

    Attributes:
        uri: Database connection string
        name: Database name
    """

    uri: SecretStr = Field(..., description="Database connection URI")
    name: str = Field(default="crfsm-peyman-2104987", description="Database name")


class RabbitMQConfig(BaseModel):
    """
    RabbitMQ configuration.

    Attributes:
        url: RabbitMQ connection URL
        queue_name: RabbitMQ queue name
        exchange_name: RabbitMQ exchange name
    """

    url: SecretStr = Field(..., description="RabbitMQ connection URL")
    queue_name: str = Field(default="crfms_queue", description="RabbitMQ queue name")
    exchange_name: str = Field(
        default="crfms_exchange", description="RabbitMQ exchange name"
    )


class SystemConfig(BaseSettings):
    """
    Main application configuration with environment-based loading.

    Read .env.example for more information about Environment Variables
    """

    # Environment
    environment: str = Field(
        default="development",
        description="Application environment (development|production|staging|test)",
    )

    # Logging Configuration with defaults
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_format: str = Field(
        default='{"ts": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "module": "%(module)s", "msg": "%(message)s"}',
        description="Log message format string",
    )

    # External Service Configurations
    database: DatabaseConfig
    rabbitmq: RabbitMQConfig

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


try:
    config = SystemConfig()
except Exception as e:
    logging.error(f"Failed to load config variables: {e}")
    sys.exit(1)
