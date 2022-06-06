import logging
import os

from project.config._config import ENVVAR_PREFIX


def cleanup_environment():
    for key, _ in os.environ.items():
        if key.startswith(ENVVAR_PREFIX + '_'):
            LOGGER.debug('Removing environment variable %s', key)
            del os.environ[key]


LOGGER = logging.getLogger(__name__)
