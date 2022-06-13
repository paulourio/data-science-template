from typing import Dict, Final
import logging

from gcsfs import GCSFileSystem

from project.config import load_config


def filesystem():
    """Return Storage filesystem."""
    config = load_config()

    assert len(config.storage.scopes) == 1

    # The scope in the config is for example
    # https://www.googleapis.com/auth/devstorage.read_write
    scope = config.storage.scopes[0].split('.')[-1]

    auth = config.storage.authentication
    token = AUTH_METHOD[auth]

    consistency = config.storage.consistency
    if consistency is None:
        consistency = 'none'

    fs = GCSFileSystem(
        project=config.gcp.project,
        access=scope,
        token=token,
        consistency=consistency,
        cache_timeout=config.storage.cache_expiration_secs,
    )

    LOGGER.debug('Initialized Storage filesystem on %s with scopes %s.',
                 config.gcp.project,
                 ', '.join([s.split('/')[-1] for s in config.storage.scopes]))

    return fs


LOGGER = logging.getLogger(__name__)

AUTH_METHOD: Final[Dict[str, str]] = {
    'default': 'google_default',
    'metadata': 'cloud',
}
"""Map storage.authentication to GCSFileSystem.token."""
