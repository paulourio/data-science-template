import os

from project.config import load_config, as_dict

from environment import cleanup_environment


def test_config_env_loader():
    """Test load from environment variables."""
    cleanup_environment()

    config = load_config(load_env=True, load_yaml=False,
                         load_command_line=False,
                         load_validate=False, load_verbose=False)
    assert as_dict(config) == {}

    os.environ.update(ENVIRONMENT)

    config = load_config(load_env=True, load_yaml=False,
                         load_command_line=False,
                         load_validate=False, load_verbose=False)
    assert as_dict(config) == CONFIG


ENVIRONMENT = {
    'APP_project__name': 'project-name',
    'APP_project__version': '@int 1',
    'APP_bigquery__scopes': (
        "['https://www.googleapis.com/auth/bigquery',"
        "'https://www.googleapis.com/auth/devstorage.read_write']"
    ),
    'APP_bigquery__location': 'US',
    'APP_bigquery__dataset': 'stage',
    'APP_bigquery__temp_dataset': 'stage',
    'APP_bigquery__cache_dataset': 'stage',
    'APP_bigquery__maximum_bytes_billed': '@int 10737418240',
    'APP_bigquery__priority': 'INTERACTIVE',
    'APP_bigquery__use_query_cache': '@bool true',
    'APP_bigquery__job_id_prefix': 'project-name-v1-',
    'APP_storage__authentication': 'google_default',
    'APP_storage__scopes': (
        "['https://www.googleapis.com/auth/devstorage.read_write']"
    ),
    'APP_storage__temp_bucket': 'project-template-temp-data',
    'APP_storage__cache_bucket': 'project-template-temp-data',
    'APP_storage__cache_seconds': '@json null',
    'APP_Labels__Service': 'project-name-service',
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
    # Dynaconf loads "Labels" as "labels", but "Service" as "Service."
    'labels': {
        'Service': 'project-name-service',
    },
}
