from __future__ import annotations

import logging
import logging.config
from typing import Any

from pythonjsonlogger.jsonlogger import JsonFormatter

from app.core.config import settings


class HealthAwareJsonFormatter(JsonFormatter):
    """Small JSON formatter that keeps logs consistent across local and container runs."""

    def add_fields(
        self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("level", record.levelname)
        log_record.setdefault("logger", record.name)
        log_record.setdefault("environment", settings.ENVIRONMENT)


def setup_logging() -> None:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": HealthAwareJsonFormatter,
                "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
            }
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "level": settings.LOG_LEVEL,
            }
        },
        "root": {"handlers": ["default"], "level": settings.LOG_LEVEL},
    }
    logging.config.dictConfig(logging_config)
