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

    fs = GCSFileSystem(
        project=config.gcp.project,
        access=scope,
        token=config.storage.authentication,
        consistency='md5',
        cache_timeout=config.storage.cache_seconds,
    )

    LOGGER.debug('Initialized Storage filesystem on %s with scopes %s.',
                 config.gcp.project,
                 ', '.join([s.split('/')[-1] for s in config.storage.scopes]))

    return fs


LOGGER = logging.getLogger(__name__)
