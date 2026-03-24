"""
Logging configuration utilities.

The LifeLine-ICT backend must provide transparent diagnostics for campus ICT
teams. This module configures Python's logging so that request handling and
service events produce structured, human-readable output.
"""

import logging
from typing import Final


LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure the root logger with a consistent format.

    Parameters
    ----------
    level:
        Logging level for the root logger. Defaults to ``logging.INFO`` because
        it provides sufficient context without overwhelming student operators.
    """

    logging.basicConfig(level=level, format=LOG_FORMAT)
