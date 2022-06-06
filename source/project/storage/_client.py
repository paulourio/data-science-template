from functools import lru_cache
import logging

from dynaconf.base import Settings
from google.cloud.storage import Client
import google.auth

from project.config import load_config


@lru_cache
def client() -> Client:
    """Return initialized Storage."""
    config = load_config()
    return make_client(config)


def make_client(config: Settings) -> Client:
    """Return a new initialized Storage client for a config."""
    credentials, _ = google.auth.default(scopes=config.storage.scopes)
    gcs = Client(
        project=config.gcp.project,
        credentials=credentials,
    )
    LOGGER.debug('Initialized Storage client on %s with scopes %s.',
                 config.gcp.project,
                 ', '.join([s.split('/')[-1] for s in config.storage.scopes]))
    return gcs


LOGGER = logging.getLogger(__name__)
