import logging
import os

from project.config._environment import Environment


def cleanup_environment():
    """Delete environment variables with a given prefix."""
    prefix = Environment.variable_prefix().upper() + '_'
    for key, _ in os.environ.items():
        if key.startswith(prefix):
            LOGGER.debug('Removing environment variable %s', key)
            del os.environ[key]


LOGGER = logging.getLogger(__name__)
