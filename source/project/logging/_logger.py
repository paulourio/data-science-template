from typing import Callable, Dict, Final
import logging
import sys

from dynaconf.base import Settings

try:
    import coloredlogs
except ImportError:
    coloredlogs = None

try:
    from google.cloud.logging import handlers as gcloud_handlers
except ImportError:
    gcloud_handlers = None


def init_logging(config: Settings) -> None:
    """Initialize logging."""
    init = LOGGERS[config.logging.type]
    init(config)
    _setup_loggers(config)


def _init_default(config: Settings):
    logging.basicConfig(
        format=config.logging.message_format,
        datefmt=config.logging.timestamp_format,
        level=config.logging.level,
        stream=sys.stdout,
    )


def _init_colored(config):
    if coloredlogs is None:
        raise ImportError('coloredlogs is not installed')

    coloredlogs.install(
        fmt=config.logging.message_format,
        datefmt=config.logging.timestamp_format,
        level=config.logging.level,
        stream=sys.stdout,
    )


def _init_google(config):
    if gcloud_handlers is None:
        raise ImportError('google-cloud-logging is not installed')

    logging.basicConfig(
        stream=sys.stdout,
        level=config.logging.level,
    )

    handler = gcloud_handlers.StructuredLogHandler(
        labels=config.labels,
        stream=sys.stdout,
        project_id=config.google.project,
    )
    logger = logging.getLogger()

    logger.addHandler(handler)


def _setup_loggers(config: Settings):
    for name, level in config.logging.loggers.items():
        logging.getLogger(name).setLevel(level)


LOGGERS: Final[Dict[str, Callable[[Settings], None]]] = {
    'default': _init_default,
    'colored': _init_colored,
    'google': _init_google,
}
