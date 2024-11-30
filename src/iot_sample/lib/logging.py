"""A general logging module for the application.

Performs basic config and sets the logging level for
a root logger.
"""

import logging

from ..iot.settings import settings

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(settings.logging_level)
