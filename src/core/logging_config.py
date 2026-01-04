"""
Application Logging Configuration

This module centralizes logging setup for the entire service.

Usage:
    from core.logging_config import setup_logging

    # Call once at application startup:
    setup_logging()

    # Then in any module:
    import logging
    logger = logging.getLogger(__name__)
    logger.info("message...")

Author: Peyman Khodabandehlouei
Last Update: 20-12-2025
"""

import logging
from logging.config import dictConfig

from core import config


def setup_logging() -> None:
    level = getattr(logging, config.log_level.value, logging.INFO)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": config.log_format,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": level,
                },
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
            "loggers": {
                "httpx": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "httpcore": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "openai": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
    )
