from yaml import load
from .config import load_config
from .logging import init_logging
from . import config, storage, bigquery


def init(**kwargs):
    config = load_config(**kwargs)
    init_logging(config)
    return config
