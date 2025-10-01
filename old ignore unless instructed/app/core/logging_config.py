import logging.config
import os
from app.core.config import settings
from pythonjsonlogger import jsonlogger

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "app.core.logging_config.CustomJsonFormatter",
        },
    },
    "handlers": {
        "default": {
            "level": settings.LOG_LEVEL,
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # root logger
            "level": settings.LOG_LEVEL,
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default"],
            "propagate": False,
        },
        "joulejournal": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default"],
            "propagate": False,
        },
    },
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = record.created
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
