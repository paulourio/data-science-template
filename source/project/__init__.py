"""Project management module."""
# flake8: noqa
from . import core
from .config import load_config
from .logging import init_logging
from . import config, storage, bigquery, pipeline


def init(**kwargs):
    """Initialize project logging and settings."""
    c = load_config(**kwargs)
    init_logging(c)
    return c
