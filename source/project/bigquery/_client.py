from functools import lru_cache
import logging

from dynaconf.base import Settings
from google.cloud.bigquery import Client, QueryJobConfig
import google.auth

from project.config import load_config


@lru_cache
def client() -> Client:
    """Return initialized BigQuery client."""
    config = load_config()
    return make_client(config)


def job_config() -> QueryJobConfig:
    """Return base Job config."""
    config = load_config()
    return make_job_config(config)


def make_client(config: Settings) -> Client:
    """Return a new initialized BigQuery client for a config."""
    credentials, _ = google.auth.default(scopes=config.bigquery.scopes)
    client = Client(
        project=config.gcp.project,
        credentials=credentials,
        location=config.bigquery.location,
        default_query_job_config=make_job_config(config),
    )
    LOGGER.debug('Initialized BigQuery client on %s with scopes %s.',
                 config.gcp.project,
                 ', '.join([s.split('/')[-1] for s in config.bigquery.scopes]))
    return client


def make_job_config(config: Settings) -> QueryJobConfig:
    """Return a BigQuery Job configuration for a config."""
    job_config = QueryJobConfig(
        default_dataset=config.bigquery.dataset,
        labels=config.labels,
        priority=config.bigquery.priority,
        parameter_mode='NAMED',
        use_legacy_sql=False,
        use_query_cache=config.bigquery.use_query_cache,
    )
    return job_config


LOGGER = logging.getLogger(__name__)

SCOPE_PREFIX = 'https://www.googleapis.com/auth/devstorage.'
