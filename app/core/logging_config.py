import logging
import sys
from logging.config import dictConfig

import uvicorn
from uvicorn.logging import DefaultFormatter

LOG_LEVEL = logging.DEBUG
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Exclude health check endpoint from logs
        return "GET /health" not in record.getMessage()


def setup_logging(log_level: int = LOG_LEVEL) -> None:
    """
    Set up logging for the application.
    """
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "health_check_filter": {
                "()": HealthCheckFilter,
            },
        },
        "formatters": {
            "default": {
                "()": DefaultFormatter,
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": True,
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(process)s %(levelname)s %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "filters": ["health_check_filter"],
            },
            "json": {
                "formatter": "json",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "filters": ["health_check_filter"],
            },
        },
        "loggers": {
            "root": {
                "handlers": ["default"],
                "level": log_level,
            },
            "uvicorn.error": {
                "level": log_level,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
        },
    }

    # Use JSON formatter if not in development
    if not __debug__:
        logging_config["loggers"]["root"]["handlers"] = ["json"]
        logging_config["loggers"]["uvicorn.access"]["handlers"] = ["json"]

    dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    """
    return logging.getLogger(name)
