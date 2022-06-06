import os

from dynaconf.base import Settings

from project.config import ConfigFormat, load_config, as_dict

from environment import cleanup_environment


def test_config_env_loader():
    """Test load from environment variables."""
    cleanup_environment()

    config = load_config(format=ConfigFormat.ENVIRONMENT_VARIABLES)
    assert as_dict(config) == {}

    os.environ.update(ENVIRONMENT)

    config = load_config(format=ConfigFormat.ENVIRONMENT_VARIABLES)
    assert as_dict(config) == CONFIG


ENVIRONMENT = {
    'PROJECT_project__name': 'project-name',
    'PROJECT_project__version': '@int 1',
    'PROJECT_bigquery__scopes': (
        "['https://www.googleapis.com/auth/bigquery',"
        "'https://www.googleapis.com/auth/devstorage.read_write']"
    ),
    'PROJECT_bigquery__location': 'US',
    'PROJECT_bigquery__dataset': 'stage',
    'PROJECT_bigquery__temp_dataset': 'stage',
    'PROJECT_bigquery__cache_dataset': 'stage',
    'PROJECT_bigquery__maximum_bytes_billed': '@int 10737418240',
    'PROJECT_bigquery__priority': 'INTERACTIVE',
    'PROJECT_bigquery__use_query_cache': '@bool true',
    'PROJECT_bigquery__job_id_prefix': 'project-name-v1-',
    'PROJECT_storage__authentication': 'google_default',
    'PROJECT_storage__scopes': (
        "['https://www.googleapis.com/auth/devstorage.read_write']"
    ),
    'PROJECT_storage__temp_bucket': 'project-template-temp-data',
    'PROJECT_storage__cache_bucket': 'project-template-temp-data',
    'PROJECT_storage__cache_seconds': '@json null',
    'PROJECT_labels__service': 'project-name-service',
}

CONFIG = {
    'project': {'version': 1, 'name': 'project-name'},
    'bigquery': {
        'cache_dataset': 'stage',
        'dataset': 'stage',
        'job_id_prefix': 'project-name-v1-',
        'location': 'US',
        'maximum_bytes_billed': 10737418240,
        'priority': 'INTERACTIVE',
        'temp_dataset': 'stage',
        'scopes': [
            'https://www.googleapis.com/auth/bigquery',
            'https://www.googleapis.com/auth/devstorage.read_write',
        ],
        'use_query_cache': True,
    },
    'storage': {
        'authentication': 'google_default',
        'cache_seconds': None,
        'cache_bucket': 'project-template-temp-data',
        'scopes': [
            'https://www.googleapis.com/auth/devstorage.read_write',
        ],
        'temp_bucket': 'project-template-temp-data',
    },
    'labels': {
        'service': 'project-name-service',
    },
}
