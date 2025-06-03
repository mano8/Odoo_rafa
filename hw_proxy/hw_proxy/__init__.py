"""hw_proxy Package"""
import logging
from typing import Optional

from hw_proxy.__version__ import VERSION


class AppFilter(logging.Filter):
    """
    Class used to add a custom entry into the logger
    """

    def filter(self, record):
        record.app_version = f"hw_proxy-{VERSION}"
        return True


class CustomFormatter(logging.Formatter):
    """Logging custom formatter."""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self,
                 fmt: str,
                 date_format: str = "%Y-%m-%d %H:%M:%S"
                 ):
        super().__init__()
        self.fmt = fmt
        self.date_format = date_format
        self.colors_format = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.WARN: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        if not hasattr(record, "app_version"):
            record.app_version = ""
        color_fmt = self.colors_format.get(
            record.levelno,
            self.colors_format[logging.INFO]
        )
        style_formatter = logging.Formatter(
            fmt=color_fmt,
            datefmt=self.datefmt,
            style="{"
        )
        return style_formatter.format(record)


def configure_logging(log_level: Optional[str] = "INFO"):
    """
    Configure the Python logger for the 'hw_proxy' module.

    Sets up a StreamHandler with a custom formatter,
    and validates the log level.

    Args:
        log_level (Optional[str]):
            Logging level to use (e.g., 'DEBUG', 'INFO').
            Defaults to 'INFO'. Must be a valid logging level name.

    Raises:
        ValueError: If log_level is not a recognized logging level.
    """
    log = logging.getLogger("hw_proxy")
    log.addFilter(AppFilter())
    log.propagate = False

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    fmt = "{asctime} :: {app_version} :: {message}"
    formatter = CustomFormatter(fmt=fmt, date_format="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    # Normalize and validate log level
    log_level = log_level.upper() if log_level else "INFO"
    if log_level not in logging._nameToLevel:
        raise ValueError(
            f"Invalid log level: '{log_level}'. "
            f"Must be one of: {', '.join(logging._nameToLevel.keys())}")

    log.setLevel(logging._nameToLevel[log_level])
    log.addHandler(handler)

    log.debug(
        f"Logger configured "
        f"with level: {log_level}"
    )
